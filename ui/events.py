# UI B — 이벤트 연결 (.click / .submit)
import gradio as gr

from ui.chat_actions import on_ask, on_clear, on_translate_history
import json

from ui.content import I18N, language_button_text, localize
from ui.font_size import LANGUAGE_JS as FONT_SIZE_LANGUAGE_JS
from ui.layout import chat_empty_html, coming_soon_html, home_hero_html

# 화면이 바뀌면 맨 위로 (긴 대화를 보다가 홈으로 돌아올 때 등)
_SCROLL_TOP_JS = "() => window.scrollTo({top: 0})"

# 언어를 바꾸면 브라우저 탭 제목도 그 언어의 서비스명으로 바꿉니다.
_APP_NAMES = {lang: t["app_name"] for lang, t in I18N.items()}
_TITLE_JS = f"(lang) => {{ document.title = {json.dumps(_APP_NAMES, ensure_ascii=False)}[lang] || document.title; }}"


def _show_screen(target, names):
    """target 화면만 보이게 하는 핸들러를 만듭니다. 채팅 기록은 숨겨질 뿐 그대로 남습니다."""
    return lambda: [gr.Column(visible=name == target) for name in names]


def bind_events(ui):
    # 질문하기 버튼, Enter, 추천 질문 버튼 모두 같은 on_ask를 씁니다.
    # 선택한 언어(language)를 입력으로 함께 넘겨 질문·답변을 그 언어로 처리합니다.
    ask_outputs = [ui["chatbot"], ui["question"]]
    ask_inputs = [ui["question"], ui["chatbot"], ui["language"]]
    ui["ask_btn"].click(on_ask, inputs=ask_inputs, outputs=ask_outputs)
    ui["question"].submit(on_ask, inputs=ask_inputs, outputs=ask_outputs)

    for btn in ui["example_btns"]:
        btn.click(on_ask, inputs=[btn, ui["chatbot"], ui["language"]], outputs=ask_outputs)

    ui["clear_btn"].click(on_clear, outputs=ask_outputs)

    # 화면 전환: 홈 메뉴 → 같은 key의 화면, 뒤로가기 아이콘 → 홈 (docs/ui-interactions-rules.md 5-4)
    screens = ui["screens"]
    names = list(screens)
    nav = dict(outputs=list(screens.values()), queue=False, show_progress="hidden")
    for key, btn in ui["menu_btns"].items():
        btn.click(_show_screen(key, names), **nav).then(None, js=_SCROLL_TOP_JS)
    for btn in ui["home_btns"]:
        btn.click(_show_screen("home", names), **nav).then(None, js=_SCROLL_TOP_JS)

    # ── 지구본 언어 메뉴 ──────────────────────────────────────────────
    lang_open = gr.State(False)  # 메뉴가 열려 있는지 (화면 전용 상태)
    i = ui["i18n"]
    menu_keys = list(ui["menu_btns"])
    title_keys = list(i["screen_titles"])

    # 언어 변경 시 글자를 바꿀 컴포넌트 순서. on_language_change의 update 순서와 반드시 같아야 합니다.
    text_targets = [
        i["home_hero"],
        *ui["menu_btns"].values(),
        *ui["home_btns"],
        *i["screen_titles"].values(),
        *i["notices"],
        *i["coming_soons"],
        ui["chatbot"],
        ui["question"],
        ui["ask_btn"],
        ui["clear_btn"],
        *ui["example_btns"],
        i["tab_chat"],
        i["tab_faq"],
        *i["faq_accordions"],
        *i["faq_answers"],
        i["source_note"],
    ]

    def toggle_lang(is_open):
        is_open = not is_open
        return is_open, gr.update(visible=is_open)

    ui["lang_btn"].click(
        toggle_lang, inputs=[lang_open], outputs=[lang_open, ui["language"]]
    )

    def on_language_change(value):
        # 선택 언어로 모든 화면 문구를 바꾸고, 메뉴를 닫고, 지구본 글자를 갱신합니다.
        t = localize(value)
        updates = [gr.update(value=home_hero_html(t))]  # home_hero
        updates += [gr.update(value=t["menu"][k]) for k in menu_keys]  # menu_btns
        updates += [gr.update(value=t["home_btn"]) for _ in ui["home_btns"]]  # home_btns
        updates += [gr.update(value=f"## {t['menu'][k]}") for k in title_keys]  # screen_titles
        updates += [gr.update(value=t["notice"]) for _ in i["notices"]]  # notices
        updates += [gr.update(value=coming_soon_html(t)) for _ in i["coming_soons"]]  # coming_soons
        updates += [
            gr.update(placeholder=chat_empty_html(t)),  # chatbot
            gr.update(placeholder=t["question_placeholder"]),  # question
            gr.update(value=t["ask_btn"]),  # ask_btn
            gr.update(value=t["clear_btn"]),  # clear_btn
        ]
        updates += [gr.update(value=q) for q in t["example_questions"]]  # example_btns
        updates += [gr.update(label=t["tab_chat"]), gr.update(label=t["tab_faq"])]
        updates += [gr.update(label=q) for q, _a in t["faq"]]  # faq_accordions
        updates += [gr.update(value=a) for _q, a in t["faq"]]  # faq_answers
        updates.append(gr.update(value=t["source_note"]))  # source_note

        # [메뉴 상태, 메뉴 닫기, 지구본 글자] + 화면 문구 update들
        return [
            False,
            gr.update(visible=False),
            gr.update(value=language_button_text(value)),
            *updates,
        ]

    ui["language"].change(
        on_language_change,
        inputs=[ui["language"]],
        outputs=[lang_open, ui["language"], ui["lang_btn"], *text_targets],
    ).then(
        # 서버를 거치지 않는 부분(글자 크기 버튼·브라우저 탭 제목)은 브라우저에서 바꿉니다.
        None, inputs=[ui["language"]], js=FONT_SIZE_LANGUAGE_JS
    ).then(None, inputs=[ui["language"]], js=_TITLE_JS).then(
        # 이미 주고받은 대화 말풍선도 새 언어로 번역합니다(OpenAI 호출이라 화면 문구보다 늦게 바뀝니다).
        on_translate_history,
        inputs=[ui["chatbot"], ui["language"]],
        outputs=[ui["chatbot"]],
    )
