# UI A — 화면 구성 (gr.Blocks, gr.Chatbot, gr.Textbox, gr.Button, gr.Row/Column)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
import gradio as gr

EXAMPLE_QUESTIONS = [
    "수습기간에도 최저임금을 다 받아야 하나요?",
    "1년 일하면 연차휴가는 며칠 생기나요?",
    "해고 예고는 며칠 전에 해야 하나요?",
]


def build_layout():
    gr.Markdown("# 노동법 ChatPDF\n근로기준법 등 노동관련법에 대해 궁금한 점을 물어보세요.")

    chatbot = gr.Chatbot(label="대화", height=480)
    with gr.Row():
        example_btns = [gr.Button(q, size="sm") for q in EXAMPLE_QUESTIONS]
    with gr.Row():
        question = gr.Textbox(
            show_label=False,
            placeholder="질문을 입력하고 Enter를 누르세요",
            scale=5,
        )
        ask_btn = gr.Button("질문하기", variant="primary", scale=1)
    clear_btn = gr.Button("대화 초기화", size="sm")

    return {
        "chatbot": chatbot,
        "question": question,
        "ask_btn": ask_btn,
        "clear_btn": clear_btn,
        "example_btns": example_btns,
    }
