# UI A — 화면 구성 (gr.Tabs, gr.Chatbot, gr.Textbox, gr.Button, gr.Row)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
# 화면 문구는 ui/content.py, 색·간격은 ui/style.css에서 고칩니다.
import gradio as gr

from ui.content import (
    APP_NAME,
    ASK_BTN,
    CHAT_PLACEHOLDER,
    CLEAR_BTN,
    DEFAULT_LANGUAGE,
    EXAMPLE_QUESTIONS,
    FAQ_ITEMS,
    LABOR_LAW_MD,
    LANGUAGES,
    NOTICE,
    QUESTION_PLACEHOLDER,
    SOURCE_NOTE,
    TAB_CHAT,
    TAB_FAQ,
    TAB_LAW,
    TAGLINE,
    language_button_text,
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
    # 맨 위 한 줄: 왼쪽은 제목, 오른쪽은 지구본 언어 선택 + 글자 크기.
    # 지구본 버튼을 누르면 그 아래로 언어 목록이 펼쳐집니다(이벤트는 ui/events.py).
    # 글자 크기는 브라우저에서만 동작합니다(ui/font_size.py).
    with gr.Row(elem_id="top-row"):
        header_md = gr.Markdown(f"# {APP_NAME}\n{TAGLINE}", elem_id="app-header", min_width=260)
        with gr.Column(elem_id="topbar", scale=0, min_width=0):
            with gr.Row(elem_id="top-controls"):
                lang_btn = gr.Button(
                    language_button_text(DEFAULT_LANGUAGE),
                    size="sm",
                    elem_id="lang-btn",
                )
                build_font_size_control()
            language = gr.Radio(
                choices=LANGUAGES,
                value=DEFAULT_LANGUAGE,
                show_label=False,
                visible=False,
                elem_id="language",
            )
    notice_md = gr.Markdown(NOTICE, elem_id="notice")

    source_notes = []  # 두 탭에 들어가는 출처·기준일 문구 (언어 바뀌면 함께 갱신)

    with gr.Tabs(elem_id="tabs"):
        with gr.Tab(TAB_CHAT, id="chat", elem_id="tab-chat") as tab_chat:
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
                    ASK_BTN, variant="primary", scale=1, min_width=96, elem_id="ask-btn"
                )
            clear_btn = gr.Button(CLEAR_BTN, size="sm", variant="secondary", elem_id="clear-btn")

        with gr.Tab(TAB_FAQ, id="faq", elem_id="tab-faq") as tab_faq:
            faq_accordions = []  # 질문(아코디언 라벨)
            faq_answers = []  # 답변(Markdown)
            for q, a in FAQ_ITEMS:
                with gr.Accordion(q, open=False, elem_classes="faq-item") as acc:
                    faq_accordions.append(acc)
                    faq_answers.append(gr.Markdown(a))
            source_notes.append(gr.Markdown(SOURCE_NOTE, elem_classes="source-note"))

        with gr.Tab(TAB_LAW, id="law", elem_id="tab-law") as tab_law:
            law_md = gr.Markdown(LABOR_LAW_MD, elem_id="labor-law")
            source_notes.append(gr.Markdown(SOURCE_NOTE, elem_classes="source-note"))

    # B가 이벤트를 걸 컴포넌트와, 언어 변경 시 글자를 바꿀 컴포넌트(i18n)를 함께 반환합니다.
    return {
        "chatbot": chatbot,
        "question": question,
        "ask_btn": ask_btn,
        "clear_btn": clear_btn,
        "example_btns": example_btns,
        "language": language,
        "lang_btn": lang_btn,
        # 언어 변경 시 갱신할 화면 문구 컴포넌트 모음 (docs/ui-layout-rules.md 4번 표)
        "i18n": {
            "header": header_md,
            "notice": notice_md,
            "tab_chat": tab_chat,
            "tab_faq": tab_faq,
            "tab_law": tab_law,
            "faq_accordions": faq_accordions,
            "faq_answers": faq_answers,
            "law_md": law_md,
            "source_notes": source_notes,
        },
    }
