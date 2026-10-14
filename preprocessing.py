import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "docs" / "노동관련법"
DB_DIR = BASE_DIR / "chroma_db"


def build_db(pdf_dir, openai_key):
    if not openai_key:
        raise ValueError(
            "OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요."
        )

    pdf_dir = Path(pdf_dir)
    if not pdf_dir.is_dir():
        raise NotADirectoryError(f"PDF 폴더가 없습니다: {pdf_dir}")

    pdf_paths = sorted(
        path
        for path in pdf_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    )
    if not pdf_paths:
        raise FileNotFoundError(f"PDF 파일이 없습니다: {pdf_dir}")

    pages = []
    for pdf_path in pdf_paths:
        pages.extend(PyPDFLoader(str(pdf_path)).load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.split_documents(pages)

    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=openai_key,
    )

    db = Chroma.from_documents(
        documents=texts,
        embedding=embeddings_model,
        collection_name="labor_laws",
        persist_directory=str(DB_DIR),
    )
    return db, f"✅ 처리 완료: {len(pages)}페이지 → {len(texts)}개 청크"


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")
    db, status = build_db(PDF_DIR, os.getenv("OPENAI_API_KEY"))
    print(status)