"""'개선 전' 측정용: 첫 커밋(b34bbdb, 수업 기본 코드)의 답변 방식을 그대로 재현합니다.

    python eval/run_eval.py --system baseline --db-dir chroma_db_backup_v1 --label before

첫 커밋과 같은 점
- 100자 / 겹침 20자로 나눈 DB (chroma_db_backup_v1, 9,344조각, text-embedding-3-large)
- 질문 확장: MultiQueryRetriever 기본 영어 프롬프트 + ChatOpenAI 기본 모델(gpt-3.5-turbo)
- 검색: as_retriever() 기본값(k=4)
- 답변: rlm/rag-prompt + gpt-4o-mini, 출처 표시 없음

다른 점
- rlm/rag-prompt는 hub.pull 대신 같은 문구를 아래에 옮겨 적었습니다. 지금 설치된 langsmith는
  공개 프롬프트를 내려받는 것을 보안상 기본으로 막기 때문입니다.
- 평가에서 '근거 페이지 적중'을 재려고, LLM에 넘긴 검색 문서를 last_context_docs에 남깁니다.
"""

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# hub.pull("rlm/rag-prompt")와 같은 문구
RAG_PROMPT = ChatPromptTemplate.from_messages([(
    "human",
    "You are an assistant for question-answering tasks. Use the following pieces of retrieved "
    "context to answer the question. If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \nContext: {context} \nAnswer:",
)])

last_context_docs = []


def answer(question, openai_key, db):
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_key)
    retriever = MultiQueryRetriever.from_llm(retriever=db.as_retriever(), llm=llm)
    generate_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_key)

    docs = retriever.invoke(question)
    last_context_docs[:] = docs
    context = "\n\n".join(doc.page_content for doc in docs)

    chain = RAG_PROMPT | generate_llm | StrOutputParser()
    text = ""
    for chunk in chain.stream({"context": context, "question": question}):
        text += chunk
        yield text
