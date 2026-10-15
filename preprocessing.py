import argparse
import hashlib
import os
import re
from bisect import bisect_right
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "docs" / "노동관련법"
DB_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "labor_laws"
EMBEDDING_MODEL = "text-embedding-3-large"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# 제17조(근로조건의 명시), 제8조의2(근로자의 요구에 따른 서면 교부) 등.
# 행 시작의 조문 제목만 인식해서 '법 제17조제2항'과 같은 본문 인용은 제외합니다.
ARTICLE_RE = re.compile(
    r"(?m)^[ \t]*(제\d+조(?:의\d+)?)\(([^)\n]{1,100})\)"
)
HEADER_RE = re.compile(r"^법제처\s+\d+\s+국가법령정보센터\s*$")


def clean_page(text, law_name):
    """각 페이지에 반복되는 법제처 머리말만 제거합니다."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if HEADER_RE.match(stripped) or stripped == law_name:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def make_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )


def page_for(offset, page_starts):
    return max(0, bisect_right(page_starts, offset) - 1)


def chunks_for_pdf(pdf_path, splitter):
    law_name = pdf_path.stem.split("(", 1)[0].strip()
    loaded = PyPDFLoader(str(pdf_path)).load()
    is_case_material = "판례" in pdf_path.stem

    page_texts = [clean_page(doc.page_content, law_name) for doc in loaded]
    page_starts = []
    parts = []
    offset = 0
    for page_text in page_texts:
        page_starts.append(offset)
        parts.append(page_text)
        offset += len(page_text) + 2  # 페이지 구분자 '\n\n'
    all_text = "\n\n".join(parts)

    matches = [] if is_case_material else list(ARTICLE_RE.finditer(all_text))
    chunks = []

    if matches:
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(all_text)
            article = all_text[start:end].strip()
            if not article:
                continue

            article_no, article_title = match.group(1), match.group(2).strip()
            heading = f"{law_name} {article_no}({article_title})"

            for piece in splitter.create_documents([article]):
                local_offset = piece.metadata.get("start_index", 0)
                begin = start + local_offset
                finish = begin + max(len(piece.page_content) - 1, 0)
                first_page = page_for(begin, page_starts)
                last_page = page_for(finish, page_starts)

                content = piece.page_content
                # 나뉜 조문의 후속 청크도 검색 가능한 제목을 갖도록 접두어 추가
                if article_no not in content[:80]:
                    content = f"{heading}\n{content}"

                chunks.append(Document(
                    page_content=content,
                    metadata={
                        "source": pdf_path.name,
                        "law_name": law_name,
                        "article_no": article_no,
                        "article_title": article_title,
                        "page": first_page,
                        "page_end": last_page,
                        "document_type": "statute",
                    },
                ))
    else:
        # 판례집처럼 제N조(제목) 체계가 없는 자료는 기존 페이지 방식 유지
        for page_no, page_text in enumerate(page_texts):
            if not page_text.strip():
                continue
            page_doc = Document(
                page_content=page_text,
                metadata={
                    "source": pdf_path.name,
                    "law_name": law_name,
                    "page": page_no,
                    "page_end": page_no,
                    "document_type": "reference",
                },
            )
            chunks.extend(splitter.split_documents([page_doc]))

    return len(loaded), chunks, len(matches)


def prepare_documents(pdf_dir):
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"PDF 폴더가 없습니다: {pdf_dir}")
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"PDF 파일이 없습니다: {pdf_dir}")

    splitter = make_splitter()
    result = []
    ids = []
    seen = set()
    total_pages = 0
    total_articles = 0

    for path in pdfs:
        page_count, chunks, article_count = chunks_for_pdf(path, splitter)
        total_pages += page_count
        total_articles += article_count
        for chunk in chunks:
            fingerprint = (
                chunk.metadata["source"],
                chunk.metadata.get("article_no", ""),
                chunk.metadata["page"],
                chunk.page_content,
            )
            digest = hashlib.sha256(repr(fingerprint).encode("utf-8")).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            result.append(chunk)
            ids.append(digest)

    return pdfs, total_pages, total_articles, result, ids


def build_db(dry_run=False):
    load_dotenv(ROOT / ".env")
    pdfs, page_count, article_count, chunks, ids = prepare_documents(PDF_DIR)
    print(
        f"[v3] PDF {len(pdfs)}개 / {page_count}페이지 / "
        f"인식한 조문 {article_count}개 / {len(chunks)}개 청크"
    )

    # 이번 프로젝트의 첫 실패 사례를 무비용으로 확인
    examples = [
        ("근로기준법", "제17조"),
        ("근로자퇴직급여 보장법", "제9조"),
        ("근로기준법", "제56조"),
        ("최저임금법", "제6조"),
    ]
    for law, article in examples:
        found = [
            doc for doc in chunks
            if doc.metadata.get("law_name") == law
            and doc.metadata.get("article_no") == article
        ]
        pages = sorted({
            page + 1
            for doc in found
            for page in range(doc.metadata["page"], doc.metadata["page_end"] + 1)
        })
        print(f"[확인] {law} {article}: {len(found)}개 청크 / p.{pages}")
        if found:
            print("       ", " ".join(found[0].page_content.split())[:180])

    if dry_run:
        print("[미리보기 완료] API 요청 및 DB 저장 없음")
        return

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError(".env에서 OPENAI_API_KEY를 확인하세요.")
    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        raise FileExistsError(f"이미 v3 DB가 존재합니다: {DB_DIR}")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=openai_key,
        chunk_size=50,
    )
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
    )
    print(f"✅ v3 DB 구축 완료: {DB_DIR.name} / {db._collection.count()}개 청크")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="조문 단위 RAG 전처리 실험")
    parser.add_argument("--dry-run", action="store_true", help="API 비용 없이 청크 검사")
    args = parser.parse_args()
    build_db(dry_run=args.dry_run)
