from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from ui.chat_actions import prepare_db
from ui.events import bind_events
from ui.content import APP_NAME
from ui.layout import THEME, build_layout

# .env 파일에서 OPENAI_API_KEY 등 환경변수를 불러옵니다.
load_dotenv()

CSS_PATH = Path(__file__).parent / "ui" / "style.css"
ASSETS_DIR = Path(__file__).parent / "ui" / "assets"

# 캐릭터 스프라이트처럼 CSS에서 불러오는 이미지를 브라우저에 공개합니다.
gr.set_static_paths(paths=[ASSETS_DIR])

with gr.Blocks(title=APP_NAME) as demo:
    ui = build_layout()
    bind_events(ui)

if __name__ == "__main__":
    prepare_db()  # 첫 질문을 기다리지 않도록 시작할 때 문서 벡터DB를 미리 만듭니다.
    demo.launch(theme=THEME, css_paths=[CSS_PATH])
