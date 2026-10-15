# 임금체불 사업주 조회 화면 — 조회는 arrears/service.py의 서비스가, 스타일은 ui/arrears.css가 맡습니다.
# 지금은 목업 데이터만 씁니다(실제 API를 호출하지 않음). 화면은 공식 명단공개 조회 결과 모양을 따릅니다.
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import gradio as gr

from arrears.service import (
    LISTED,
    NOT_FOUND,
    NOT_LISTED,
    get_lookup_service,
    normalize_business_number,
)

MOCK_NOTICE = "목업 데이터"
LOADING_TEXT = "사업장 정보를 불러오고 있어요"

STATUS_TEXT = {
    LISTED: (
        "명단공개 대상",
        "입력한 사업자등록번호의 사업장이 고용노동부 체불사업주 명단공개 대상에 포함되어 있어요.",
    ),
    NOT_LISTED: (
        "명단공개 기록 없음",
        "이 사업장은 체불사업주 명단공개 대상에 없어요. "
        "<strong>명단공개는 일정 기준을 넘는 경우에만 이뤄지므로, 체불 이력이 없다는 뜻은 아닙니다.</strong>",
    ),
    NOT_FOUND: (
        "조회 결과 없음",
        "입력한 사업자등록번호와 일치하는 사업장을 찾지 못했어요. "
        "<strong>명단에 없다거나 체불 이력이 없다는 뜻은 아닙니다.</strong>",
    ),
}

# 명단 기록 한 건의 항목: (화면 이름, mock_data의 키)
RECORD_FIELDS = [
    ("사업장명", "company"),
    ("사업주", "owner"),
    ("소재지", "address"),
    ("업종", "industry"),
    ("체불액", "amount"),
    ("명단공개 기간", "period"),
    ("위반 내용", "violation"),
]

CHECKS = {
    LISTED: [
        "근로계약서에 적힌 사업장명·대표자·소재지가 위 기록과 같은지 대조하세요.",
        "체불이 걱정되면 근로계약서·임금명세서를 꼭 받아 두고, 임금 지급일을 확인해 두세요.",
        "명단공개는 기간이 정해져 있어, 공개 기간이 끝난 기록은 보이지 않을 수 있어요.",
    ],
    NOT_LISTED: [
        "명단공개는 일정 기준을 넘는 경우에만 이뤄지므로, 명단에 없어도 체불이 있었을 수 있어요.",
        "공식 누리집에서 사업장을 다시 확인하고, 필요하면 고용노동부에 문의하세요.",
        "근로계약서·임금명세서를 받아 두고 임금 지급일을 확인해 두세요.",
    ],
    NOT_FOUND: [
        "사업자등록번호 10자리를 빠짐없이, 순서대로 입력했는지 확인하세요.",
        "폐업·법인 전환 등으로 사업자등록번호가 바뀌었을 수 있어요.",
        "실제 정보는 공식 누리집에서 직접 조회하세요.",
    ],
}

OFFICIAL_GUIDE = """
<ul>
  <li>체불사업주 명단공개는 <a href="https://www.moel.go.kr" target="_blank" rel="noopener">고용노동부 누리집</a>에서 확인할 수 있어요.</li>
  <li>고용 관련 공공서비스는 <a href="https://www.work24.go.kr" target="_blank" rel="noopener">고용24</a>에서 이용할 수 있어요.</li>
  <li>임금체불 상담·신고: 고용노동부 고객상담센터 <strong>국번 없이 1350</strong></li>
</ul>
"""


def _record_html(record):
    rows = "".join(
        f"<dt>{name}</dt><dd>{escape(record.get(key, '-'))}</dd>" for name, key in RECORD_FIELDS
    )
    return f'<dl class="arrears-record">{rows}</dl>'


def render_result(result):
    """LookupResult → 결과 화면 HTML. 사용자가 입력한 글자는 escape해서 넣습니다."""
    label, summary = STATUS_TEXT[result.status]
    records = ""
    if result.records:
        records = "<h4>명단공개 내역</h4>" + "".join(_record_html(r) for r in result.records)
    checks = "".join(f"<li>{c}</li>" for c in CHECKS[result.status])
    queried_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y.%m.%d %H:%M")
    mock_badge = f'<span class="arrears-mock-badge">{MOCK_NOTICE}</span>' if result.is_mock else ""

    return f"""
<div class="arrears-result arrears-{result.status}">
  <div class="arrears-head">
    <span class="arrears-head-title">체불사업주 명단공개 조회</span>
    {mock_badge}
  </div>
  <dl class="arrears-query">
    <dt>사업자등록번호</dt><dd>{escape(result.business_number)}</dd>
  </dl>
  <h4>조회 결과</h4>
  <p><span class="arrears-status">{label}</span></p>
  <p>{summary}</p>
  {records}
  <p class="arrears-meta">조회 일시 {queried_at}</p>
  <h4>추가 확인이 필요한 사항</h4>
  <ul>{checks}</ul>
  <h4>공식 정보 확인 안내</h4>
  {OFFICIAL_GUIDE}
</div>
"""


def on_lookup(business_number):
    digits = normalize_business_number(business_number)
    if digits is None:
        return '<p class="arrears-empty">사업자등록번호 10자리를 입력해 주세요. (예: 000-00-00000)</p>'
    result = get_lookup_service().lookup(digits)
    return render_result(result)


def build_arrears_tab(loading_html):
    """loading_html(문구)는 ui/layout.py의 judge_loading_html — 조회하는 동안 결과 자리에 판사 애니메이션을 띄웁니다."""
    gr.Markdown("### 일하기 전에 사업장을 확인해 보세요")
    business_number = gr.Textbox(
        label="사업자등록번호",
        placeholder="숫자 10자리 (하이픈 없이 입력해도 돼요)",
        max_length=12,
        elem_id="arrears-number",
    )
    btn = gr.Button("조회하기", variant="primary", elem_id="arrears-btn")

    out = gr.HTML(padding=False, elem_id="arrears-result")

    # 조회하는 동안: Gradio 기본 로딩 표시 대신 결과 자리 가운데에 판사 + 안내 문구
    loading = loading_html(LOADING_TEXT)
    for event in (btn.click, business_number.submit):
        event(lambda: loading, None, out, queue=False, show_progress="hidden").then(
            on_lookup, business_number, out, show_progress="hidden"
        )
