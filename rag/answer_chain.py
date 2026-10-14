
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


def answer(question, openai_key, db):
    # 1. 질문 및 DB 확인
    if not question or not question.strip():
        raise ValueError("질문을 입력해 주세요.")

    if db is None:
        raise ValueError("법률 데이터베이스가 없습니다.")

    if not openai_key:
        raise ValueError("OpenAI API 키가 없습니다.")

    # 2. LLM 준비
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=openai_key
    )

    # 3. 관련 법률 검색
    retriever = MultiQueryRetriever.from_llm(
        retriever=db.as_retriever(search_kwargs={"k": 4}),
        llm=llm
    )

    # 4. 기본 RAG 프롬프트
    prompt = ChatPromptTemplate.from_template("""
    제공된 참고 문서만을 기반으로 질문에 답변하세요.
    문서에서 확인할 수 없는 내용은 추측하지 마세요.

    [참고 문서]
    {context}

    [질문]
    {question}
    """)

    # 5. 검색된 문서 내용 정리
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 6. RAG 체인 구성
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # 7. 스트리밍 답변 생성
    text = ""
    for chunk in rag_chain.stream(question):
        text += chunk
        yield text
