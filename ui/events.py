# UI B — 이벤트 연결 (.click / .submit)
from ui.chat_actions import on_ask, on_clear


def bind_events(ui):
    # 질문하기 버튼, Enter, 추천 질문 버튼 모두 같은 on_ask를 씁니다.
    ask_outputs = [ui["chatbot"], ui["question"]]
    ask_inputs = [ui["question"], ui["chatbot"]]
    ui["ask_btn"].click(on_ask, inputs=ask_inputs, outputs=ask_outputs)
    ui["question"].submit(on_ask, inputs=ask_inputs, outputs=ask_outputs)

    for btn in ui["example_btns"]:
        btn.click(on_ask, inputs=[btn, ui["chatbot"]], outputs=ask_outputs)

    ui["clear_btn"].click(on_clear, outputs=ask_outputs)
