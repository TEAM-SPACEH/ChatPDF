# 최저임금 계산기 탭 — 계산 결과는 모달 창으로 띄웁니다.
# 계산 로직은 wage/calc.py, 모달 스타일은 ui/style.css에 있습니다.
import gradio as gr

from wage import calc as wc

OFFICIAL_LINK = "[최저임금위원회에서 다시 확인하기](https://www.minimumwage.go.kr)"


def calculate(year, pay_type, amount, weekly_hours, daily_hours, five_or_more, probation):
    if not amount or amount <= 0:
        return "받은 금액을 입력해 주세요."
    year = int(year)
    if pay_type == "시급":
        r = wc.check_hourly(year, amount, probation)
    elif pay_type == "일당":
        if not daily_hours or daily_hours <= 0:
            return "하루 근무시간을 입력해 주세요."
        r = wc.check_daily(year, amount, daily_hours, five_or_more, probation)
    else:
        if not weekly_hours or weekly_hours <= 0:
            return "주 근무시간을 입력해 주세요."
        r = wc.check_monthly(year, amount, weekly_hours, probation)
    return wc.format_result(r) + "\n\n" + OFFICIAL_LINK


def open_modal(*inputs):
    return calculate(*inputs), gr.update(visible=True)


def close_modal():
    return gr.update(visible=False)


def toggle_inputs(pay_type):
    return (gr.update(visible=pay_type == "월급"),
            gr.update(visible=pay_type == "일당"),
            gr.update(visible=pay_type == "일당"))


def build_wage_tab():
    years = sorted(wc.MINIMUM_WAGES, reverse=True)
    gr.Markdown("### 내 임금이 최저임금보다 적은지 확인해 보세요")
    with gr.Row():
        year = gr.Dropdown([str(y) for y in years], value=str(years[0]), label="연도")
        pay_type = gr.Radio(["시급", "일당", "월급"], value="일당", label="임금 형태")
    amount = gr.Number(label="받은 금액(원)", precision=0)
    weekly_hours = gr.Number(label="주 근무시간(주휴 제외)", value=40, visible=False)
    daily_hours = gr.Number(label="하루 근무시간", value=8)
    five_or_more = gr.Checkbox(label="직원이 5명 이상인 사업장", value=True)
    probation = gr.Checkbox(label="수습 기간 중(3개월 이내)", value=False)
    btn = gr.Button("계산하기", variant="primary")

    with gr.Column(visible=False, elem_id="wage-modal") as modal:
        with gr.Column(elem_id="wage-modal-box"):
            gr.Markdown("### 계산 결과", elem_id="wage-modal-title")
            out = gr.Markdown(elem_id="wage-result")
            close_btn = gr.Button("닫기", elem_id="wage-close")

    pay_type.change(toggle_inputs, pay_type, [weekly_hours, daily_hours, five_or_more])
    btn.click(open_modal,
              [year, pay_type, amount, weekly_hours, daily_hours, five_or_more, probation],
              [out, modal])
    close_btn.click(close_modal, None, modal)
