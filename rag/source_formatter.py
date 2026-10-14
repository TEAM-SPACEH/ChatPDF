def format_sources(docs):
    sources = []
    seen = set()

    for doc in docs:
        metadata = doc.metadata

        # PDF 메타데이터 가져오기
        law_name = metadata.get("law_name")
        article = metadata.get("article")
        source = metadata.get("source")
        page = metadata.get("page")

        # 파일 경로에서 파일명만 추출
        filename = ""
        if source:
            filename = str(source).replace("\\", "/").split("/")[-1]

        # 페이지 번호 처리 (0부터 시작)
        page_text = None
        if isinstance(page, int) and page >= 0:
            page_text = f"p.{page + 1}"

        # 실제 존재하는 정보만 출처에 포함
        parts = []

        if law_name:
            parts.append(str(law_name))

        if article:
            parts.append(str(article))

        if filename:
            parts.append(filename)

        if page_text:
            parts.append(page_text)

        if not parts:
            continue

        source_text = " · ".join(parts)

        # 중복 출처 제거
        if source_text not in seen:
            seen.add(source_text)
            sources.append(f"- {source_text}")

    if not sources:
        return "검색된 참고 문서가 없습니다."

    return "\n".join(sources)