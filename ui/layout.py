# UI A — 화면 구성 (gr.Tabs, gr.Chatbot, gr.Textbox, gr.Button, gr.Row)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
# 화면 문구는 ui/content.py, 색·간격은 ui/style.css에서 고칩니다.
import gradio as gr

from ui.content import (
    APP_NAME,
    CHAT_PLACEHOLDER,
    EXAMPLE_QUESTIONS,
    FAQ_ITEMS,
    LABOR_LAW_MD,
    NOTICE,
    QUESTION_PLACEHOLDER,
    SOURCE_NOTE,
    TAGLINE,
)
from ui.font_size import build_font_size_control

# 테마 — "계약서를 형광펜으로 검토하는" 느낌: 흰 종이, 남색 잉크, 노란 형광펜(style.css).
# Gradio 6에서는 app.py의 demo.launch(theme=...)로 적용합니다.
INK = "#1B2A41"
INK_SOFT = "#5B6576"
PAPER = "#F7F8FA"
RULE = "#DDE1E8"

THEME = gr.themes.Base(
    neutral_hue="slate",
    # Pretendard는 style.css의 @import로 불러오고, 여기서는 이름만 지정합니다.
    font=["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
).set(
    body_background_fill=PAPER,
    body_text_color=INK,
    body_text_color_subdued=INK_SOFT,
    border_color_primary=RULE,
    color_accent=INK,
    color_accent_soft="#E9EDF4",
    color_accent_soft_dark="#1E2A3D",
    block_radius="14px",
    block_shadow="none",
    block_border_color=RULE,
    input_radius="12px",
    input_shadow="none",
    input_background_fill="#FFFFFF",
    input_border_color=RULE,
    input_border_width="1px",
    input_border_color_focus=INK,
    button_large_radius="12px",
    button_medium_radius="12px",
    button_small_radius="999px",
    button_primary_background_fill=INK,
    button_primary_background_fill_hover="#2A3D5C",
    button_primary_text_color="#FFFFFF",
    button_primary_border_color=INK,
    button_primary_border_color_hover="#2A3D5C",
    button_primary_border_color_dark="#D6DEEC",
    button_primary_background_fill_dark="#D6DEEC",
    button_primary_background_fill_hover_dark="#FFFFFF",
    button_primary_text_color_dark="#101826",
    button_primary_shadow="none",
    button_secondary_shadow="none",
)


def build_layout():
    with gr.Row(elem_id="top-row"):
        gr.Markdown(f"# {APP_NAME}\n{TAGLINE}", elem_id="app-header", min_width=260)
        build_font_size_control()
    gr.Markdown(NOTICE, elem_id="notice")

    with gr.Tabs(elem_id="tabs"):
        with gr.Tab("질문하기", id="chat", elem_id="tab-chat"):
            chatbot = gr.Chatbot(
                show_label=False,
                height=440,
                placeholder=CHAT_PLACEHOLDER,
                elem_id="chatbot",
            )
            with gr.Row(elem_id="example-row"):
                example_btns = [
                    gr.Button(q, size="sm", elem_classes="example-btn")
                    for q in EXAMPLE_QUESTIONS
                ]
            with gr.Row(elem_id="input-row"):
                question = gr.Textbox(
                    show_label=False,
                    placeholder=QUESTION_PLACEHOLDER,
                    scale=5,
                    elem_id="question",
                )
                ask_btn = gr.Button(
                    "질문하기", variant="primary", scale=1, min_width=96, elem_id="ask-btn"
                )
            clear_btn = gr.Button("대화 지우기", size="sm", variant="secondary", elem_id="clear-btn")

        with gr.Tab("자주 묻는 질문", id="faq", elem_id="tab-faq"):
            for q, a in FAQ_ITEMS:
                with gr.Accordion(q, open=False, elem_classes="faq-item"):
                    gr.Markdown(a)
            gr.Markdown(SOURCE_NOTE, elem_classes="source-note")

        with gr.Tab("법령 요약", id="law", elem_id="tab-law"):
            gr.Markdown(LABOR_LAW_MD, elem_id="labor-law")
            gr.Markdown(SOURCE_NOTE, elem_classes="source-note")

    # B가 이벤트를 걸 컴포넌트만 반환합니다. (docs/ui-layout-rules.md 4번 표)
    return {
        "chatbot": chatbot,
        "question": question,
        "ask_btn": ask_btn,
        "clear_btn": clear_btn,
        "example_btns": example_btns,
    }
