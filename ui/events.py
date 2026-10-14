# UI B — 이벤트 연결 (.click / .submit, gr.State)
import gradio as gr

from ui.chat_actions import on_ask


def bind_events(ui):
    # PDF 업로드 화면을 제거했으므로 벡터DB는 만들지 않습니다.
    # db_state는 빈 값(None)으로 두고, 답변은 모델 지식 기반으로 생성합니다.
    db_state = gr.State()

    ask_inputs = [ui["question"], db_state]
    ui["ask_btn"].click(on_ask, inputs=ask_inputs, outputs=ui["output"])
    ui["question"].submit(on_ask, inputs=ask_inputs, outputs=ui["output"])
