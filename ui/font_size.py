# UI A — 글자 크기 조절 (작게 / 보통 / 조금 크게 / 크게 / 가장 크게)
# "글자 크기 : 보통 ⌄" 버튼을 누르면 목록이 열립니다. 고용노동부 「AI 노동법 상담」의 방식을 참고했습니다.
# 서버를 거치지 않고 브라우저에서만 동작합니다. 그래서 ui/events.py와 key 표와는 관계없습니다.
# 고른 단계는 <html data-font-size="...">로 표시하고, 실제 크기는 ui/style.css에서 정합니다.
# 버튼·목록 글자는 ui/content.py의 I18N에 있고, 언어를 바꾸면 LANGUAGE_JS가 브라우저에서 바꿔 끼웁니다.
import json

import gradio as gr

from ui.content import DEFAULT_LANGUAGE, I18N, localize

STORAGE_KEY = "nodong-font-size"
DEFAULT_SIZE = "md"

# 단계 값. 순서대로 목록에 나오고, 이름은 I18N[언어]["font_sizes"]의 같은 순서입니다.
# 배율은 style.css의 html[data-font-size] 규칙에 있습니다.
SIZES = ["sm", "md", "lg", "xl", "xxl"]
_KO = localize(DEFAULT_LANGUAGE)
FONT_SIZES = list(zip(SIZES, _KO["font_sizes"]))

_OPTIONS = "".join(
    f'<li role="option" id="font-size-{size}" data-size="{size}" data-label="{label}" aria-selected="false" tabindex="-1">'
    f'<span class="font-size-sample" aria-hidden="true">{_KO["font_sample"]}</span>'
    f'<span class="font-size-name">{label}</span></li>'
    for size, label in FONT_SIZES
)

_HTML = (
    '<div class="font-size-control">'
    '<button type="button" class="font-size-toggle" aria-haspopup="listbox" aria-expanded="false">'
    f'<span class="font-size-label">{_KO["font_size_label"]}</span> '
    f'<span class="font-size-current">{dict(FONT_SIZES)[DEFAULT_SIZE]}</span>'
    '<span class="font-size-chevron" aria-hidden="true"></span>'
    "</button>"
    f'<ul class="font-size-menu" role="listbox" aria-label="{_KO["font_size_label"].rstrip(" :：")}" hidden>{_OPTIONS}</ul>'
    "</div>"
)

# 저장된 단계를 불러와 적용하고, 목록에서 고르면 바꾼 뒤 저장합니다.
# 마우스 클릭과 키보드(↑↓ 이동, Enter·Space 선택, Esc 닫기) 모두 됩니다.
# 시크릿 창처럼 localStorage를 못 쓰는 환경에서도 화면은 그대로 동작하게 try로 감쌉니다.
_JS = f"""
const KEY = "{STORAGE_KEY}";
const DEFAULT = "{DEFAULT_SIZE}";
const root = document.documentElement;
const toggle = element.querySelector(".font-size-toggle");
const current = element.querySelector(".font-size-current");
const menu = element.querySelector(".font-size-menu");
const options = Array.from(menu.querySelectorAll("[role=option]"));
const sizes = options.map((o) => o.dataset.size);

function apply(size) {{
  if (size === DEFAULT) delete root.dataset.fontSize;
  else root.dataset.fontSize = size;
  options.forEach((o) => o.setAttribute("aria-selected", String(o.dataset.size === size)));
  const picked = options.find((o) => o.dataset.size === size);
  current.textContent = picked.dataset.label;
}}

function open() {{
  menu.hidden = false;
  toggle.setAttribute("aria-expanded", "true");
  (options.find((o) => o.getAttribute("aria-selected") === "true") || options[0]).focus();
}}

function close(focusToggle) {{
  menu.hidden = true;
  toggle.setAttribute("aria-expanded", "false");
  if (focusToggle) toggle.focus();
}}

// 키보드로 고른 경우에만 버튼으로 포커스를 돌려서, 마우스로 고른 뒤에는 포커스 테두리가 남지 않게 합니다.
function choose(option, byKeyboard) {{
  apply(option.dataset.size);
  try {{ localStorage.setItem(KEY, option.dataset.size); }} catch (e) {{}}
  close(byKeyboard);
}}

let saved = DEFAULT;
try {{ saved = localStorage.getItem(KEY) || DEFAULT; }} catch (e) {{}}
apply(sizes.includes(saved) ? saved : DEFAULT);

toggle.addEventListener("click", () => (menu.hidden ? open() : close(false)));
options.forEach((o) => o.addEventListener("click", () => choose(o, false)));

menu.addEventListener("keydown", (e) => {{
  const i = options.indexOf(document.activeElement);
  if (e.key === "ArrowDown") {{ e.preventDefault(); options[Math.min(i + 1, options.length - 1)].focus(); }}
  else if (e.key === "ArrowUp") {{ e.preventDefault(); options[Math.max(i - 1, 0)].focus(); }}
  else if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); if (i >= 0) choose(options[i], true); }}
  else if (e.key === "Escape" || e.key === "Tab") {{ close(e.key === "Escape"); }}
}});

// 목록 바깥을 누르면 닫습니다.
document.addEventListener("click", (e) => {{
  if (!menu.hidden && !element.contains(e.target)) close(false);
}});
"""


def build_font_size_control():
    return gr.HTML(_HTML, js_on_load=_JS, elem_id="font-size", padding=False)


# 언어를 바꾸면 ui/events.py가 .then(js=LANGUAGE_JS)로 부릅니다. 서버를 거치지 않고 글자만 바꿉니다.
# 고른 단계는 그대로 두고, 버튼에 보이는 현재 단계 이름도 새 언어로 바꿉니다.
_LABELS = {
    lang: {
        "label": t["font_size_label"],
        "sizes": dict(zip(SIZES, t["font_sizes"])),
        "sample": t["font_sample"],
    }
    for lang, t in I18N.items()
}
LANGUAGE_JS = f"""
(lang) => {{
  const all = {json.dumps(_LABELS, ensure_ascii=False)};
  const t = all[lang] || all["{DEFAULT_LANGUAGE}"];
  document.querySelectorAll(".font-size-control").forEach((el) => {{
    el.querySelector(".font-size-label").textContent = t.label;
    el.querySelector(".font-size-menu").setAttribute("aria-label", t.label.replace(/[\\s:：]+$/, ""));
    el.querySelectorAll("[role=option]").forEach((o) => {{
      o.dataset.label = t.sizes[o.dataset.size];
      o.querySelector(".font-size-name").textContent = o.dataset.label;
      o.querySelector(".font-size-sample").textContent = t.sample;
      if (o.getAttribute("aria-selected") === "true") {{
        el.querySelector(".font-size-current").textContent = o.dataset.label;
      }}
    }});
  }});
}}
"""
