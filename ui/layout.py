# UI A — 화면 구성 (gr.Tabs, gr.Chatbot, gr.Textbox, gr.Button, gr.Row)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
# 화면 문구는 ui/content.py, 색·간격은 ui/style.css에서 고칩니다.
from pathlib import Path

import gradio as gr

from ui.content import (
    APP_NAME,
    ASK_BTN,
    CLEAR_BTN,
    DEFAULT_LANGUAGE,
    EXAMPLE_QUESTIONS,
    FAQ_ITEMS,
    HOME_BTN,
    LANGUAGES,
    MENU_ITEMS,
    NOTICE,
    QUESTION_PLACEHOLDER,
    SOURCE_NOTE,
    TAB_CHAT,
    TAB_FAQ,
    language_button_text,
    localize,
)
from ui.font_size import build_font_size_control
from ui.wage_tab import build_wage_tab

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
    # 국기 전용 폰트를 맨 앞에 둡니다. 국기 이모지 글자에만 쓰이고(unicode-range) 나머지 글자는 Pretendard로 나옵니다.
    font=[
        "Twemoji Country Flags",
        "Pretendard Variable",
        "Pretendard",
        "-apple-system",
        "system-ui",
        "sans-serif",
    ],
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
# 앱 로고 (홈 맨 위). 판사 캐릭터와 서비스명이 그려진 어두운 배경의 배너 한 장입니다.
LOGO_URL = "/gradio_api/file=ui/assets/logo-banner.webp"

# 아래 HTML 조각은 언어를 바꿀 때 ui/events.py가 같은 함수로 다시 만들어 끼웁니다.
# t는 ui/content.py의 localize(언어)가 돌려주는 문구 묶음입니다.


def chat_empty_html(t):
    """대화가 비어 있을 때: 판사 캐릭터가 말풍선으로 인사하고 아래에 사용 안내"""
    return f"""
<div class="judge-hero">
  <p class="judge-hero-bubble">{t["judge_greeting"]}</p>
  <div class="judge-hero-figure" role="img" aria-label="{t['judge_alt']}"></div>
  <p class="judge-hero-guide">{"<br>".join(t["chat_placeholder"])}</p>
</div>
"""


def home_hero_html(t):
    """홈 맨 위 가운데: 앱 로고(판사 캐릭터가 함께 그려진 배너 한 장) + 한 줄 소개.
    로고가 곧 서비스명(h1)입니다. 로고 글자는 한국어라서, 다른 언어일 때는 그 언어의 서비스명을 함께 보여줍니다."""
    name = (
        "" if t["app_name"] == APP_NAME else f'<p class="home-name">{t["app_name"]}</p>'
    )
    return f"""
<div class="home-hero">
  <h1 class="home-logo"><img src="{LOGO_URL}" alt="{t['app_name']}"></h1>
  {name}
  <p>{t["tagline"]}</p>
</div>
"""


def coming_soon_html(t):
    """아직 준비 중인 화면: 판사가 말풍선으로 안내"""
    return f"""
<div class="judge-hero coming-soon">
  <p class="judge-hero-bubble">{t["coming_soon"]}</p>
  <div class="judge-hero-figure" role="img" aria-label="{t['judge_alt']}"></div>
</div>
"""


_KO = localize(DEFAULT_LANGUAGE)
MENU_LABELS = dict(MENU_ITEMS)


def _screen_bar(key):
    """각 화면 위쪽 바: 왼쪽 뒤로가기 아이콘 + 가운데 화면 이름.
    (뒤로가기 버튼, 화면 이름, 면책 고지)를 돌려줍니다. 버튼은 B가 이벤트를, 글자는 언어 변경을 겁니다."""
    with gr.Row(elem_classes="screen-bar"):
        # 글자는 화면에서 숨기고 아이콘만 보입니다(style.css). 화면 낭독기는 이 글자를 읽습니다.
        home_btn = gr.Button(HOME_BTN, scale=0, min_width=44, elem_classes="home-btn")
        title = gr.Markdown(f"## {MENU_LABELS[key]}", elem_classes="screen-title")
    notice = gr.Markdown(NOTICE, elem_classes="notice")
    return home_btn, title, notice


def _top_controls():
    """모든 화면 맨 위 오른쪽: 지구본 언어 선택 + 글자 크기.
    지구본 버튼을 누르면 그 아래로 언어 목록이 펼쳐집니다(이벤트는 ui/events.py).
    글자 크기는 브라우저에서만 동작합니다(ui/font_size.py)."""
    with gr.Column(elem_id="topbar"):
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
    return lang_btn, language


def build_layout():
    lang_btn, language = _top_controls()

    # ───────── 홈 ─────────
    with gr.Column(visible=True, elem_id="screen-home") as home_screen:
        home_hero = gr.HTML(home_hero_html(_KO), padding=False)
        with gr.Column(elem_id="home-menu"):
            menu_btns = {
                key: gr.Button(label, elem_id=f"menu-{key}", elem_classes="menu-btn")
                for key, label in MENU_ITEMS
            }
        home_notice = gr.Markdown(NOTICE, elem_classes="notice")

    # ───────── 노동법 챗봇 (탭 2개) ─────────
    with gr.Column(visible=False, elem_id="screen-chat") as chat_screen:
        chat_bar = _screen_bar("chat")
        chat = _chat_tabs()

    # ───────── 준비 중인 화면 ─────────
    with gr.Column(visible=False, elem_id="screen-villain") as villain_screen:
        villain_bar = _screen_bar("villain")
        villain_soon = gr.HTML(coming_soon_html(_KO), padding=False)

    # ───────── 최저임금 계산기 (화면·이벤트는 ui/wage_tab.py) ─────────
    with gr.Column(visible=False, elem_id="screen-calc") as calc_screen:
        calc_bar = _screen_bar("calc")
        build_wage_tab()

    bars = {"chat": chat_bar, "villain": villain_bar, "calc": calc_bar}
    i18n = chat.pop("i18n")

    # B가 이벤트를 걸 컴포넌트와, 언어 변경 시 글자를 바꿀 컴포넌트(i18n)를 함께 반환합니다.
    # (docs/ui-layout-rules.md 4번 표)
    return {
        **chat,
        "screens": {
            "home": home_screen,
            "chat": chat_screen,
            "villain": villain_screen,
            "calc": calc_screen,
        },
        "menu_btns": menu_btns,
        "home_btns": [bar[0] for bar in bars.values()],
        "language": language,
        "lang_btn": lang_btn,
        "i18n": {
            **i18n,
            "home_hero": home_hero,
            # 화면 key → 그 화면 위쪽 바의 이름(Markdown)
            "screen_titles": {key: bar[1] for key, bar in bars.items()},
            "notices": [home_notice, *(bar[2] for bar in bars.values())],
            "coming_soons": [villain_soon],
        },
    }


def _chat_tabs():
    """노동법 챗봇 화면의 탭 2개(질문하기·자주 묻는 질문). 채팅 컴포넌트를 dict로 돌려줍니다."""
    with gr.Tabs(elem_id="tabs"):
        with gr.Tab(TAB_CHAT, id="chat", elem_id="tab-chat") as tab_chat:
            chatbot = gr.Chatbot(
                show_label=False,
                height="56vh",
                min_height=380,
                placeholder=chat_empty_html(_KO),
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
                    ASK_BTN, variant="primary", scale=1, min_width=96, elem_id="ask-btn"
                )
            clear_btn = gr.Button(
                CLEAR_BTN, size="sm", variant="secondary", elem_id="clear-btn"
            )

        with gr.Tab(TAB_FAQ, id="faq", elem_id="tab-faq") as tab_faq:
            faq_accordions = []  # 질문(아코디언 라벨)
            faq_answers = []  # 답변(Markdown)
            for q, a in FAQ_ITEMS:
                with gr.Accordion(q, open=False, elem_classes="faq-item") as acc:
                    faq_accordions.append(acc)
                    faq_answers.append(gr.Markdown(a))
            source_note = gr.Markdown(SOURCE_NOTE, elem_classes="source-note")

    return {
        "chatbot": chatbot,
        "question": question,
        "ask_btn": ask_btn,
        "clear_btn": clear_btn,
        "example_btns": example_btns,
        "i18n": {
            "tab_chat": tab_chat,
            "tab_faq": tab_faq,
            "faq_accordions": faq_accordions,
            "faq_answers": faq_answers,
            "source_note": source_note,
        },
    }
