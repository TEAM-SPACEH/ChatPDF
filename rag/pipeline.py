# RAG 담당 — PDF 벡터DB 구축(build_db)과 질문 검색·답변 생성(answer)
# UI 쪽(ui/)에서는 이 두 함수만 호출합니다. 청킹·검색·프롬프트 튜닝은 이 파일에서 진행하세요.
# OpenAI 키는 UI 입력란을 없앴으므로 환경변수 OPENAI_API_KEY에서 읽습니다.
import os
import uuid

import gradio as gr
from langchain import hub
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_db(pdf_path, openai_key):
    if not openai_key:
        return None, "⚠️ OpenAI API 키를 먼저 입력한 뒤 PDF를 다시 올려주세요."
    if pdf_path is None:
        return None, ""

    pages = PyPDFLoader(pdf_path).load_and_split()

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
        texts, embeddings_model, collection_name=f"pdf_{uuid.uuid4().hex}"
    )
    return db, f"✅ 처리 완료: {len(pages)}페이지 → {len(texts)}개 청크"


SYSTEM_PROMPT = (
    "당신은 한국 비정규직(기간제·단시간) 근로자의 근로계약을 돕는 상담 챗봇입니다. "
    "근로기준법과 「기간제 및 단시간근로자 보호 등에 관한 법률」에 근거해 "
    "쉽고 정확하게 한국어로 답하세요. 확실하지 않은 내용은 단정하지 말고, "
    "필요하면 고용노동부 고객상담센터(☎1350) 등 공식 창구를 안내하세요."
)


def answer(question, db):
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise gr.Error(
            "서버에 OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다. "
            "앱 실행 전 키를 설정해주세요."
        )
    if not question:
        raise gr.Error("질문을 입력하세요.")

    # PDF 업로드 화면을 제거해 db가 없을 수 있습니다.
    # db가 없으면 모델 지식으로 일반 상담을 제공합니다.
    if db is None:
        chat_llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, openai_api_key=openai_key
        )
        messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(question)]
        text = ""
        for chunk in chat_llm.stream(messages):
            text += chunk.content
            yield text
        return

    llm = ChatOpenAI(temperature=0, openai_api_key=openai_key)
    retriever_from_llm = MultiQueryRetriever.from_llm(
        retriever=db.as_retriever(), llm=llm
    )
    prompt = hub.pull("rlm/rag-prompt")
    generate_llm = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, openai_api_key=openai_key
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever_from_llm | format_docs, "question": RunnablePassthrough()}
        | prompt
        | generate_llm
        | StrOutputParser()
    )

    text = ""
    for chunk in rag_chain.stream(question):
        text += chunk
        yield text
