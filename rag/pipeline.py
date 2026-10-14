# RAG 담당 — PDF 벡터DB 구축(build_db)과 질문 검색·답변 생성(answer)
# UI 쪽(ui/)에서는 이 두 함수만 호출합니다. 청킹·검색·프롬프트 튜닝은 이 파일에서 진행하세요.
import uuid

import gradio as gr
from langchain import hub
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
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


def answer(question, openai_key, db):
    if db is None:
        raise gr.Error("먼저 API 키를 입력하고 PDF를 업로드하세요.")
    if not question:
        raise gr.Error("질문을 입력하세요.")

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
