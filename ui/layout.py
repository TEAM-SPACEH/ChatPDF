# UI A — 화면 구성 (gr.Tabs, gr.Chatbot, gr.Textbox, gr.Button, gr.Row)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
# 화면 문구는 ui/content.py, 색·간격은 ui/style.css에서 고칩니다.
from pathlib import Path

import gradio as gr

from ui.content import (
    APP_NAME,
    CHAT_PLACEHOLDER,
    EXAMPLE_QUESTIONS,
    FAQ_ITEMS,
    JUDGE_GREETING,
    LABOR_LAW_MD,
    NOTICE,
    QUESTION_PLACEHOLDER,
    SOURCE_NOTE,
    TAGLINE,
)

# 테마 — "판사봉 캐릭터" 톤: 가발 크림 배경, 법복 차콜 글자, 버건디 포인트 하나.
# 색 근거는 docs/ui-tone-redesign-spec.md. Gradio 6에서는 app.py의 demo.launch(theme=...)로 적용합니다.
PAPER = "#FAF8F5"
SURFACE = "#FFFFFF"
INK = "#2B2523"
INK_SOFT = "#6E645E"
RULE = "#E8E3DE"
ACCENT = "#7A2E3A"
ACCENT_HOVER = "#8F3A47"
ACCENT_SOFT = "#F5EBEC"
ACCENT_SOFT_BORDER = "#EAD5D8"

# 다크 모드 — 같은 색을 뒤집어서 (포인트는 로즈)
PAPER_DARK = "#1C1817"
SURFACE_DARK = "#252120"
INK_DARK = "#EDE8E3"
INK_SOFT_DARK = "#A89F98"
RULE_DARK = "#3A3432"
ACCENT_DARK = "#E3A3AC"
ACCENT_HOVER_DARK = "#EDBBC2"
ACCENT_SOFT_DARK = "#3A2629"
ACCENT_SOFT_BORDER_DARK = "#4A3135"

THEME = gr.themes.Base(
    neutral_hue="stone",
    # Pretendard는 style.css의 @import로 불러오고, 여기서는 이름만 지정합니다.
    font=["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
).set(
    body_background_fill=PAPER,
    body_background_fill_dark=PAPER_DARK,
    body_text_color=INK,
    body_text_color_dark=INK_DARK,
    body_text_color_subdued=INK_SOFT,
    body_text_color_subdued_dark=INK_SOFT_DARK,
    border_color_primary=RULE,
    border_color_primary_dark=RULE_DARK,
    background_fill_primary=SURFACE,
    background_fill_primary_dark=SURFACE_DARK,
    # 채팅창 안쪽 면 — 회색 대신 카드와 같은 흰 면
    background_fill_secondary=SURFACE,
    background_fill_secondary_dark=SURFACE_DARK,
    color_accent=ACCENT,
    color_accent_soft=ACCENT_SOFT,
    color_accent_soft_dark=ACCENT_SOFT_DARK,
    # 질문 말풍선 테두리 (기본값은 파란색)
    border_color_accent_subdued=ACCENT_SOFT_BORDER,
    border_color_accent_subdued_dark=ACCENT_SOFT_BORDER_DARK,
    block_background_fill=SURFACE,
    block_background_fill_dark=SURFACE_DARK,
    block_radius="12px",
    block_shadow="none",
    block_border_color=RULE,
    block_border_color_dark=RULE_DARK,
    input_radius="12px",
    input_shadow="none",
    input_background_fill=SURFACE,
    input_background_fill_dark=SURFACE_DARK,
    input_border_color=RULE,
    input_border_color_dark=RULE_DARK,
    input_border_width="1px",
    input_border_color_focus=ACCENT,
    input_border_color_focus_dark=ACCENT_DARK,
    button_large_radius="12px",
    button_medium_radius="12px",
    button_small_radius="999px",
    button_primary_background_fill=ACCENT,
    button_primary_background_fill_hover=ACCENT_HOVER,
    button_primary_text_color="#FFFFFF",
    button_primary_border_color=ACCENT,
    button_primary_border_color_hover=ACCENT_HOVER,
    button_primary_background_fill_dark=ACCENT_DARK,
    button_primary_background_fill_hover_dark=ACCENT_HOVER_DARK,
    button_primary_text_color_dark=PAPER_DARK,
    button_primary_border_color_dark=ACCENT_DARK,
    button_primary_border_color_hover_dark=ACCENT_HOVER_DARK,
    button_primary_shadow="none",
    button_secondary_shadow="none",
)

# 답변 옆에 붙는 판사 얼굴. 로딩 중 전신 애니메이션은 style.css의 .judge-busy가 맡습니다.
JUDGE_AVATAR = Path(__file__).parent / "assets" / "judge-avatar.webp"

# 대화가 비어 있을 때: 판사 캐릭터가 말풍선으로 인사하고 아래에 사용 안내
CHAT_EMPTY_HTML = f"""
<div class="judge-hero">
  <p class="judge-hero-bubble">{JUDGE_GREETING}</p>
  <div class="judge-hero-figure" role="img" aria-label="판사 캐릭터"></div>
  <p class="judge-hero-guide">{"<br>".join(CHAT_PLACEHOLDER)}</p>
</div>
"""


def build_layout():
    gr.Markdown(f"# {APP_NAME}\n{TAGLINE}", elem_id="app-header")
    gr.Markdown(NOTICE, elem_id="notice")

    with gr.Tabs(elem_id="tabs"):
        with gr.Tab("질문하기", id="chat", elem_id="tab-chat"):
            chatbot = gr.Chatbot(
                show_label=False,
                height="56vh",
                min_height=380,
                placeholder=CHAT_EMPTY_HTML,
                avatar_images=(None, JUDGE_AVATAR),
                buttons=["copy"],
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
