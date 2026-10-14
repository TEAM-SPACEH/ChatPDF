
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from rag.source_formatter import format_sources


def answer(question, openai_key, db):
    # 1. 입력값 확인
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

    # 3. 관련 법률 문서 검색
    retriever = MultiQueryRetriever.from_llm(
        retriever=db.as_retriever(search_kwargs={"k": 4}),
        llm=llm
    )

    # 원본 Document 보관 (페이지 및 법률 정보 포함)
    docs = retriever.invoke(question)

    if not docs:
        yield "관련 법률 문서를 찾지 못했습니다."
        return

    # 4. 검색된 문서 내용 정리
    context = "\n\n".join(doc.page_content for doc in docs)

    # 5. RAG 프롬프트
    prompt = ChatPromptTemplate.from_template("""
    제공된 참고 문서만을 기반으로 질문에 답변하세요.
    문서에서 확인할 수 없는 내용은 추측하지 마세요.

    [참고 문서]
    {context}

    [질문]
    {question}
    """)

    # 6. LCEL 체인 구성
    rag_chain = prompt | llm | StrOutputParser()

    # 7. 답변 스트리밍
    text = ""

    for chunk in rag_chain.stream({
        "context": context,
        "question": question
    }):
        text += chunk
        yield text

    # 8. 검색된 참고 문서 표시
    sources = format_sources(docs)

    yield f"{text}\n\n---\n**검색된 참고 문서**\n{sources}"