"""청크 설정 실험용 벡터DB를 만듭니다.

    python eval/chunk_experiment.py --dry-run          # 조각 수만 세기 (API 호출 없음)
    python eval/chunk_experiment.py char500            # chroma_db_chunk_char500/ 만들기 (임베딩 비용 발생)
    python eval/run_eval.py --db-dir chroma_db_chunk_char500 --label chunk-char500

청크 나누기만 바꾸고 나머지(질문 확장·근거 선별·답변)는 지금 코드 그대로 씁니다.
- charN: 조문 경계를 무시하고 글자 수(chunk_size / chunk_overlap)로만 자름
- 조문 단위(지금 main): preprocessing.py가 조문 제목으로 나누고, 긴 조문만 800 / 150으로 더 자름 → chroma_db/

문자 단위 조각에는 조문 번호가 없어서 '출처 정확도(핵심 조문 인용)'는 비교하지 않고,
정답률·근거 페이지 적중·모름 처리·응답 시간으로 비교합니다.
머리말 제거와 페이지 계산은 preprocessing.py의 함수를 그대로 써서 조건을 맞춥니다.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain_community.document_loaders import PyPDFLoader  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

import preprocessing  # noqa: E402

# 이름: (chunk_size, chunk_overlap)
CONFIGS = {
    "char100": (100, 20),    # 수업 기본값
    "char500": (500, 50),
    "char1000": (1000, 100),
}


def char_chunks(pdf_path, chunk_size, chunk_overlap):
    law_name = pdf_path.stem.split("(", 1)[0].strip()
    page_texts = [preprocessing.clean_page(d.page_content, law_name) for d in PyPDFLoader(str(pdf_path)).load()]

    page_starts, offset = [], 0
    for text in page_texts:
        page_starts.append(offset)
        offset += len(text) + 2  # 페이지 구분자 '\n\n'
    all_text = "\n\n".join(page_texts)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True,
    )
    docs = []
    for piece in splitter.create_documents([all_text]):
        begin = piece.metadata.get("start_index", 0)
        finish = begin + max(len(piece.page_content) - 1, 0)
        docs.append(Document(
            page_content=piece.page_content,
            metadata={
                "law_name": law_name,
                "source": str(pdf_path),
                "page": preprocessing.page_for(begin, page_starts),
                "page_end": preprocessing.page_for(finish, page_starts),
            },
        ))
    return docs


def build_chunks(name):
    size, overlap = CONFIGS[name]
    chunks = []
    for pdf in sorted(preprocessing.PDF_DIR.glob("*.pdf")):
        chunks += char_chunks(pdf, size, overlap)
    return chunks


def db_dir(name):
    return ROOT / f"chroma_db_chunk_{name}"


def build_db(name):
    from dotenv import load_dotenv
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings

    out = db_dir(name)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"이미 있습니다: {out}")
    load_dotenv(ROOT / ".env")
    chunks = build_chunks(name)
    ids = [hashlib.sha256(f"{d.metadata['source']}|{d.metadata['page']}|{i}".encode()).hexdigest()
           for i, d in enumerate(chunks)]
    Chroma.from_documents(
        documents=chunks,
        # 한 요청에 보내는 조각 수를 줄여 OpenAI 임베딩 요청당 토큰 한도(30만)를 넘지 않게 합니다.
        embedding=OpenAIEmbeddings(model=preprocessing.EMBEDDING_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"),
                                   chunk_size=100),
        ids=ids,
        collection_name=preprocessing.COLLECTION_NAME,
        persist_directory=str(out),
    )
    print(f"✅ {out.name}: {len(chunks)}개 조각")


def main(argv=None):
    parser = argparse.ArgumentParser(description="청크 설정 실험용 DB 만들기")
    parser.add_argument("names", nargs="*", help=f"만들 설정 (기본: 전부) — {', '.join(CONFIGS)}")
    parser.add_argument("--dry-run", action="store_true", help="조각 수와 평균 길이만 출력 (API 호출 없음)")
    args = parser.parse_args(argv)

    names = args.names or list(CONFIGS)
    unknown = [n for n in names if n not in CONFIGS]
    if unknown:
        parser.error(f"알 수 없는 설정: {unknown} (가능: {', '.join(CONFIGS)})")
    for name in names:
        if args.dry_run:
            chunks = build_chunks(name)
            avg = sum(len(c.page_content) for c in chunks) / len(chunks)
            print(f"{name} {CONFIGS[name]}: {len(chunks)}개 조각, 평균 {avg:.0f}자")
        else:
            build_db(name)


if __name__ == "__main__":
    main()
