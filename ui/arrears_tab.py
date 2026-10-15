# 임금체불 사업주 조회 화면 — 조회는 arrears/service.py의 서비스가, 스타일은 ui/arrears.css가 맡습니다.
# 지금은 테스트용 가상 데이터만 씁니다(실제 API를 호출하지 않음).
from html import escape

import gradio as gr

from arrears.mock_data import DEMO_SCENARIOS
from arrears.service import (
    LISTED,
    NOT_FOUND,
    NOT_LISTED,
    get_lookup_service,
    normalize_business_number,
)

MOCK_NOTICE = "테스트용 가상 데이터이며 실제 사업주 정보가 아닙니다."

STATUS_TEXT = {
    LISTED: (
        "가상 명단 기록 있음",
        "테스트용 가상 데이터에서 입력한 사업자등록번호와 일치하는 가상 명단 기록을 찾았어요. "
        "아래 내용은 시연을 위해 지어낸 것입니다.",
    ),
    NOT_LISTED: (
        "가상 데이터에 기록 없음",
        "테스트용 가상 데이터에는 이 사업장의 명단 기록이 없어요. "
        "<strong>이것은 실제로 임금체불 이력이 없다는 뜻이 아닙니다.</strong> "
        "가상 데이터는 몇 개의 예시만 담고 있습니다.",
    ),
    NOT_FOUND: (
        "일치하는 사업장 없음",
        "입력한 사업자등록번호와 일치하는 사업장을 테스트용 가상 데이터에서 찾지 못했어요. "
        "<strong>실제 명단에 없다거나 체불 이력이 없다는 뜻이 아닙니다.</strong>",
    ),
}

CHECKS = {
    LISTED: [
        "실제 명단은 공식 누리집에서 사업장명·사업주명·소재지를 함께 대조해 확인하세요.",
        "근로계약서에 적힌 사업자등록번호와 입력한 번호가 같은지 다시 확인하세요.",
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


def _mock_banner():
    return f'<p class="arrears-mock-banner" role="note">⚠️ {MOCK_NOTICE}<br><span>실제 API를 조회하지 않은 시연용 결과입니다.</span></p>'


def render_result(result):
    """LookupResult → 결과 화면 HTML. 사용자가 입력한 글자는 escape해서 넣습니다."""
    label, summary = STATUS_TEXT[result.status]
    records = ""
    if result.records:
        rows = "".join(
            f"<li>{escape(r['period'])} · {escape(r['amount'])}"
            f"<br>{escape(r['detail'])}</li>"
            for r in result.records
        )
        records = f'<h4>가상 명단 기록</h4><ul class="arrears-records">{rows}</ul>'
    checks = "".join(f"<li>{c}</li>" for c in CHECKS[result.status])

    return f"""
<div class="arrears-result arrears-{result.status}">
  {_mock_banner()}
  <dl class="arrears-query">
    <dt>입력한 사업자등록번호</dt><dd>{escape(result.business_number)}</dd>
  </dl>
  <h4>조회 상태 및 결과 요약</h4>
  <p><span class="arrears-status">{label}</span></p>
  <p>{summary}</p>
  {records}
  <h4>추가 확인이 필요한 사항</h4>
  <ul>{checks}</ul>
  <h4>공식 정보 확인 안내</h4>
  {OFFICIAL_GUIDE}
  {_mock_banner()}
</div>
"""


def on_lookup(business_number):
    digits = normalize_business_number(business_number)
    if digits is None:
        return '<p class="arrears-empty">사업자등록번호 10자리를 입력해 주세요. (예: 000-00-00000)</p>'
    result = get_lookup_service().lookup(digits)
    return render_result(result)


def build_arrears_tab():
    gr.Markdown("### 일하기 전에 사업장을 확인해 보세요")
    gr.HTML(
        f'<p class="arrears-mock-banner" role="note">🧪 지금은 <strong>목업(시연) 모드</strong>입니다. {MOCK_NOTICE}</p>',
        padding=False,
    )
    business_number = gr.Textbox(
        label="사업자등록번호",
        placeholder="숫자 10자리 (하이픈 없이 입력해도 돼요)",
        max_length=12,
        elem_id="arrears-number",
    )
    btn = gr.Button("조회하기", variant="primary", elem_id="arrears-btn")

    gr.Markdown("시연용 예시 — 누르면 입력란이 채워지고 바로 조회됩니다.", elem_classes="arrears-demo-label")
    with gr.Row(elem_id="arrears-demo-row"):
        demo_btns = [
            (gr.Button(f"{label} · {number}", size="sm", elem_classes="example-btn"), number)
            for label, number in DEMO_SCENARIOS
        ]

    out = gr.HTML(padding=False, elem_id="arrears-result")

    btn.click(on_lookup, business_number, out)
    business_number.submit(on_lookup, business_number, out)
    for demo_btn, number in demo_btns:
        demo_btn.click(lambda n=number: (n, on_lookup(n)), None, [business_number, out])
