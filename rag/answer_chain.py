from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from sqlalchemy import text

from rag.prompts import get_labor_law_prompt, get_query_expansion_prompt
from rag.source_formatter import format_sources

from rag.evidence_selector import select_evidence


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
    # 일상어 질문을 법률 용어 검색 질문으로 바꿔 함께 검색합니다 (원래 질문도 포함)
    retriever = MultiQueryRetriever.from_llm(
        retriever=db.as_retriever(search_kwargs={"k": 6}),
        llm=llm,
        prompt=get_query_expansion_prompt(),
        include_original=True
    )

    # 검색된 원본 Document 보관 (메타데이터 포함)
    docs = retriever.invoke(question)

    if not docs:
        yield "관련 법률 문서를 찾지 못했습니다."
        return

    # 질문과 직접 관련된 법률 근거 선별
    selected_docs = select_evidence(question, docs, llm)

    if not selected_docs:
        yield "제공된 법률 문서에서 질문에 적용할 근거를 확인하지 못했습니다."
        return

    # 선별된 법률 근거만 LLM에 전달
    context = "\n\n".join(
        f"법률명: {doc.metadata.get('law_name', '미확인')}\n"
        f"조항: {doc.metadata.get('article_no', '미확인')}\n"
        f"조항 제목: {doc.metadata.get('article_title', '')}\n"
        f"법률 내용:\n{doc.page_content}"
        for doc in selected_docs
    )

    # 5. 노동법 특화 프롬프트
    prompt = get_labor_law_prompt()

    # 6. LCEL 체인 구성
    rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    # 7. 답변 스트리밍
    text = ""

    for chunk in rag_chain.stream({
        "context": context,
        "question": question
    }):
        text += chunk
        yield text

    # 8. 검색된 참고 문서 출처 표시
    sources = format_sources(selected_docs)
    yield f"{text}\n\n---\n**선별된 참고 조항**\n{sources}"