def format_sources(docs):
    sources = []
    seen = set()

    for doc in docs:
        metadata = doc.metadata

        # PDF에 저장된 메타데이터 가져오기
        law_name = metadata.get("law_name", "법률명 미확인")
        article = metadata.get("article")
        source = metadata.get("source", "문서명 미확인")
        page = metadata.get("page")

        # 파일 경로에서 파일명만 추출
        filename = str(source).replace("\\", "/").split("/")[-1]

        # PyPDFLoader의 페이지 번호는 0부터 시작
        if isinstance(page, int) and page >= 0:
            page_text = f"p.{page + 1}"
        else:
            page_text = "페이지 미확인"

        # 출처 정보 구성
        parts = [str(law_name)]

        if article:
            parts.append(str(article))

        parts.extend([filename, page_text])
        source_text = " · ".join(parts)

        # 중복 출처 제거
        if source_text not in seen:
            seen.add(source_text)
            sources.append(f"- {source_text}")

    if not sources:
        return "검색된 참고 문서가 없습니다."

    return "\n".join(sources)