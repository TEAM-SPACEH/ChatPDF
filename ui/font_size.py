# UI A — 글자 크기 조절 (보통 / 크게 / 아주 크게)
# 서버를 거치지 않고 브라우저에서만 동작합니다. 그래서 ui/events.py와 key 표와는 관계없습니다.
# 고른 단계는 <html data-font-size="lg|xl">로 표시하고, 실제 크기는 ui/style.css에서 정합니다.
import gradio as gr

STORAGE_KEY = "nodong-font-size"

# (단계 값, 버튼 글자). "md"가 기본입니다.
FONT_SIZES = [("md", "보통"), ("lg", "크게"), ("xl", "아주 크게")]

_HTML = (
    '<div class="font-size-control" role="group" aria-label="글자 크기">'
    '<span class="font-size-label">글자 크기</span>'
    + "".join(
        f'<button type="button" data-size="{size}" aria-pressed="false">{label}</button>'
        for size, label in FONT_SIZES
    )
    + "</div>"
)

# 저장된 단계를 불러와 적용하고, 버튼을 누르면 바꾼 뒤 저장합니다.
# 시크릿 창처럼 localStorage를 못 쓰는 환경에서도 화면은 그대로 동작하게 try로 감쌉니다.
_JS = f"""
const KEY = "{STORAGE_KEY}";
const root = document.documentElement;
const buttons = Array.from(element.querySelectorAll("button[data-size]"));
const sizes = buttons.map((b) => b.dataset.size);

function apply(size) {{
  if (size === "md") delete root.dataset.fontSize;
  else root.dataset.fontSize = size;
  buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.size === size)));
}}

let saved = "md";
try {{ saved = localStorage.getItem(KEY) || "md"; }} catch (e) {{}}
apply(sizes.includes(saved) ? saved : "md");

buttons.forEach((b) => b.addEventListener("click", () => {{
  apply(b.dataset.size);
  try {{ localStorage.setItem(KEY, b.dataset.size); }} catch (e) {{}}
}}));
"""


def build_font_size_control():
    return gr.HTML(_HTML, js_on_load=_JS, elem_id="font-size")
