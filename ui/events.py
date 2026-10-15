# UI B — 이벤트 연결 (.click / .submit)
import gradio as gr

from ui.chat_actions import on_ask, on_clear

# 화면이 바뀌면 맨 위로 (긴 대화를 보다가 홈으로 돌아올 때 등)
_SCROLL_TOP_JS = "() => window.scrollTo({top: 0})"


def _show_screen(target, names):
    """target 화면만 보이게 하는 핸들러를 만듭니다. 채팅 기록은 숨겨질 뿐 그대로 남습니다."""
    return lambda: [gr.Column(visible=name == target) for name in names]


def bind_events(ui):
    # 질문하기 버튼, Enter, 추천 질문 버튼 모두 같은 on_ask를 씁니다.
    ask_outputs = [ui["chatbot"], ui["question"]]
    ask_inputs = [ui["question"], ui["chatbot"]]
    ui["ask_btn"].click(on_ask, inputs=ask_inputs, outputs=ask_outputs)
    ui["question"].submit(on_ask, inputs=ask_inputs, outputs=ask_outputs)

    for btn in ui["example_btns"]:
        btn.click(on_ask, inputs=[btn, ui["chatbot"]], outputs=ask_outputs)

    ui["clear_btn"].click(on_clear, outputs=ask_outputs)

    # 화면 전환: 홈 메뉴 → 같은 key의 화면, 뒤로가기 아이콘 → 홈 (docs/ui-interactions-rules.md 5-4)
    screens = ui["screens"]
    names = list(screens)
    nav = dict(outputs=list(screens.values()), queue=False, show_progress="hidden")
    for key, btn in ui["menu_btns"].items():
        btn.click(_show_screen(key, names), **nav).then(None, js=_SCROLL_TOP_JS)
    for btn in ui["home_btns"]:
        btn.click(_show_screen("home", names), **nav).then(None, js=_SCROLL_TOP_JS)
