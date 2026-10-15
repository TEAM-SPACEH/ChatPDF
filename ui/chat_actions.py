# UI B — 이벤트 핸들러 (RAG 결과를 화면에 맞게 가공)
# 스트리밍 반영, 로딩·오류 처리, 대화 초기화 등은 여기서 구현합니다.
# 출처 표시는 RAG의 answer()가 마지막 답변에 붙여서 돌려줍니다 (rag/source_formatter.py).
import os
import re
import threading
from pathlib import Path

import gradio as gr
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from rag.answer_chain import answer
from rag.translate import translate
from ui.content import DEFAULT_LANGUAGE

try:
    # 로컬에서는 .env의 OPENAI_API_KEY를 읽습니다. (Spaces에서는 Secrets가 환경변수로 들어옵니다)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# preprocessing.py(RAG 담당)가 미리 만들어 둔 벡터DB 위치. 저장할 때와 같은 설정이어야 합니다.
DB_DIR = Path(os.getenv("CHROMA_DB_DIR", Path(__file__).parent.parent / "chroma_db"))
COLLECTION_NAME = "labor_laws"
EMBEDDING_MODEL = "text-embedding-3-large"

# .judge-busy는 화면에 안 보이는 표식입니다. 이게 채팅창에 있는 동안 캐릭터가 움직입니다(ui/style.css).
_BUSY = '<span class="judge-busy"></span>'
LOADING_TEXT = f"{_BUSY}⏳ 답변을 찾는 중..."
TRANSLATING_Q_TEXT = f"{_BUSY}⏳ 질문을 번역하는 중..."
TRANSLATING_TEXT = f"{_BUSY}⏳ 답변을 번역하는 중..."
_API_KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_\-*]{4,}")

# 앱 전체에서 한 번만 불러오는 벡터DB (사용자마다 새로 불러오지 않습니다)
_db = None
_db_error = ""
_db_lock = threading.Lock()


def _openai_key():
    return os.getenv("OPENAI_API_KEY", "").strip()


def prepare_db():
    """chroma_db/에 저장된 벡터DB를 한 번 불러옵니다. 이미 불러왔으면 그대로 씁니다."""
    global _db, _db_error
    with _db_lock:
        if _db is not None:
            return _db

        if not _openai_key():
            _db_error = "OPENAI_API_KEY가 설정되지 않았어요. .env 파일을 확인해 주세요."
        elif not DB_DIR.exists():
            _db_error = f"벡터DB가 없어요. 먼저 `python preprocessing.py`로 {DB_DIR}를 만들어 주세요."
        else:
            try:
                db = Chroma(
                    collection_name=COLLECTION_NAME,
                    persist_directory=str(DB_DIR),
                    embedding_function=OpenAIEmbeddings(
                        model=EMBEDDING_MODEL, openai_api_key=_openai_key()
                    ),
                )
                # 내부 속성(_collection) 대신 공개 API로 청크 수를 셉니다.
                count = len(db.get(include=[])["ids"])
                if count == 0:
                    _db_error = f"'{COLLECTION_NAME}' 컬렉션이 비어 있어요. preprocessing.py를 다시 실행해 주세요."
                else:
                    _db, _db_error = db, ""
                    print(f"[ChatPDF] 벡터DB 불러옴: {COLLECTION_NAME} ({count}개 청크)")
            except Exception as e:
                _db_error = f"벡터DB를 불러오는 중 오류가 발생했어요: {_mask_secret(str(e))}"

        if _db_error:
            print(f"[ChatPDF] {_db_error}")
        return _db


def _full(gen):
    """스트리밍 제너레이터에서 누적된 마지막(=전체) 텍스트만 받아옵니다."""
    text = ""
    for text in gen:
        continue
    return text


def on_ask(question, history, language):
    question = (question or "").strip()
    if not question:
        raise gr.Error("질문을 입력하세요.")
    # answer()는 제너레이터라 첫 yield 전까지 오류가 나지 않으므로 여기서 먼저 확인합니다.
    db = prepare_db()
    if db is None:
        raise gr.Error(_db_error)

    key = _openai_key()
    target = language or DEFAULT_LANGUAGE
    # 한국어를 고르면 번역 없이 기존 방식 그대로 동작합니다.
    translating = target != "Korean"

    history = list(history or [])
    user_idx = len(history)
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": LOADING_TEXT})
    yield history, ""

    # 1. 질문을 한국어로 번역 (RAG는 한국어 문서로 검색/답변하므로)
    rag_question = question
    if translating:
        history[-1] = {"role": "assistant", "content": TRANSLATING_Q_TEXT}
        yield history, ""
        try:
            q_ko = _full(translate(question, "Korean", key)).strip()
        except Exception as e:
            history[-1] = {
                "role": "assistant",
                "content": f"⚠️ 질문 번역 중 오류가 발생했어요: {_mask_secret(str(e))}",
            }
            yield history, ""
            return
        rag_question = q_ko or question
        # 번역된 한국어 질문을 사용자 말풍선에 함께 보여줍니다.
        history[user_idx] = {
            "role": "user",
            "content": f"{question}\n\n> 🇰🇷 {rag_question}",
        }
        history[-1] = {"role": "assistant", "content": LOADING_TEXT}
        yield history, ""

    # 2. RAG 답변 (한국어). 한국어 선택 시엔 바로 스트리밍으로 보여줍니다.
    try:
        ko_answer = ""
        for ko_answer in answer(rag_question, key, db):
            if not ko_answer:
                continue  # 첫 조각이 빈 문자열이면 로딩 문구를 유지합니다.
            if not translating:
                # answer()는 누적된 전체 텍스트를 돌려주므로 덮어씁니다.
                history[-1] = {"role": "assistant", "content": ko_answer}
                yield history, ""
    except Exception as e:
        history[-1] = {
            "role": "assistant",
            "content": f"⚠️ 답변 생성 중 오류가 발생했어요: {_mask_secret(str(e))}",
        }
        yield history, ""
        return

    if not ko_answer:
        history[-1] = {
            "role": "assistant",
            "content": "답변을 생성하지 못했어요. 질문을 바꿔서 다시 시도해 주세요.",
        }
        yield history, ""
        return

    if not translating:
        return  # 한국어는 이미 스트리밍으로 출력했습니다.

    # 3. 한국어 답변을 선택한 언어로 번역해 출력합니다.
    history[-1] = {"role": "assistant", "content": TRANSLATING_TEXT}
    yield history, ""
    try:
        text = ""
        for text in translate(ko_answer, target, key):
            if not text:
                continue
            history[-1] = {"role": "assistant", "content": text}
            yield history, ""
    except Exception as e:
        history[-1] = {
            "role": "assistant",
            "content": f"⚠️ 답변 번역 중 오류가 발생했어요: {_mask_secret(str(e))}",
        }
        yield history, ""
        return

    if not text:
        history[-1] = {
            "role": "assistant",
            "content": "번역하지 못했어요. 잠시 후 다시 시도해 주세요.",
        }
        yield history, ""


def on_clear():
    # 벡터DB는 그대로 두므로 초기화 후에도 바로 다시 질문할 수 있습니다.
    return [], ""


def _mask_secret(message):
    key = _openai_key()
    if key:
        message = message.replace(key, "***")
    return _API_KEY_PATTERN.sub("sk-***", message)
