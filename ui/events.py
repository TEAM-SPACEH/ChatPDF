# UI B — 이벤트 연결 (.click / .submit / .upload, gr.State)
import gradio as gr

from ui.chat_actions import on_ask, on_upload


def bind_events(ui):
    db_state = gr.State()

    ui["pdf_file"].upload(
        on_upload,
        inputs=[ui["pdf_file"], ui["openai_key"]],
        outputs=[db_state, ui["status"]],
    )

    ask_inputs = [ui["question"], ui["openai_key"], db_state]
    ui["ask_btn"].click(on_ask, inputs=ask_inputs, outputs=ui["output"])
    ui["question"].submit(on_ask, inputs=ask_inputs, outputs=ui["output"])
