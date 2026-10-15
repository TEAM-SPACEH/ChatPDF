# RAG — 답변 번역
# 메인 화면에서 마지막 답변을 일본어/영어/중국어로 번역합니다.
# answer()와 같은 방식으로, 지금까지 누적된 전체 텍스트를 yield 합니다.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_TRANSLATE_PROMPT = ChatPromptTemplate.from_template("""
You are a professional translator for Korean labor-law guidance.

Translate the text below into {target_language}.

[Rules]
1. Translate naturally so a worker can understand it easily.
2. Keep Markdown formatting (headings, lists, bold, horizontal rules) unchanged.
3. Keep law names, article numbers, phone numbers, URLs, and document/file names as they are.
4. Output only the translation. Do not add explanations or notes.

[Text]
{text}
""")


def translate(text, target_language, openai_key):
    # 1. 입력값 확인
    if not text or not text.strip():
        raise ValueError("번역할 내용이 없습니다.")

    if not target_language:
        raise ValueError("번역할 언어가 지정되지 않았습니다.")

    if not openai_key:
        raise ValueError("OpenAI API 키가 없습니다.")

    # 2. LLM 준비 (answer_chain.py와 같은 모델)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=openai_key,
    )

    # 3. 번역 체인
    chain = _TRANSLATE_PROMPT | llm | StrOutputParser()

    # 4. 스트리밍 (누적된 전체 텍스트를 돌려줍니다)
    text_out = ""
    for chunk in chain.stream({"target_language": target_language, "text": text}):
        text_out += chunk
        yield text_out
