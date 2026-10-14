# UI B — 이벤트 핸들러 (RAG 결과를 화면에 맞게 가공)
# 스트리밍 반영, 출처 표시, 로딩·오류 처리, 대화 초기화 등은 여기서 구현합니다.
from rag.pipeline import answer, build_db


def on_upload(pdf_path, openai_key):
    return build_db(pdf_path, openai_key)


def on_ask(question, openai_key, db):
    yield from answer(question, openai_key, db)
