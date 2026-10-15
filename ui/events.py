# UI B — 이벤트 연결 (.click / .submit)
import gradio as gr

from ui.chat_actions import on_ask, on_clear
from ui.content import language_button_text, localize


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

    # ── 지구본 언어 메뉴 ──────────────────────────────────────────────
    lang_open = gr.State(False)  # 메뉴가 열려 있는지 (화면 전용 상태)
    i = ui["i18n"]

    # 언어 변경 시 글자를 바꿀 컴포넌트 순서. on_language_change의 update 순서와 반드시 같아야 합니다.
    text_targets = [
        i["header"],
        i["notice"],
        ui["chatbot"],
        ui["question"],
        ui["ask_btn"],
        ui["clear_btn"],
        *ui["example_btns"],
        i["tab_chat"],
        i["tab_faq"],
        i["tab_law"],
        *i["faq_accordions"],
        *i["faq_answers"],
        i["law_md"],
        *i["source_notes"],
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
        updates = [
            gr.update(value=f"# {t['app_name']}\n{t['tagline']}"),  # header
            gr.update(value=t["notice"]),  # notice
            gr.update(placeholder=t["chat_placeholder"]),  # chatbot
            gr.update(placeholder=t["question_placeholder"]),  # question
            gr.update(value=t["ask_btn"]),  # ask_btn
            gr.update(value=t["clear_btn"]),  # clear_btn
        ]
        updates += [gr.update(value=q) for q in t["example_questions"]]  # example_btns
        updates += [
            gr.update(label=t["tab_chat"]),
            gr.update(label=t["tab_faq"]),
            gr.update(label=t["tab_law"]),
        ]
        updates += [gr.update(label=q) for q, _a in t["faq"]]  # faq_accordions
        updates += [gr.update(value=a) for _q, a in t["faq"]]  # faq_answers
        updates.append(gr.update(value=t["law_md"]))  # law_md
        updates += [gr.update(value=t["source_note"]) for _ in i["source_notes"]]  # source_notes

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
    )
