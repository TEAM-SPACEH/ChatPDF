from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from ui.chat_actions import prepare_db
from ui.events import bind_events
from ui.layout import THEME, build_layout

# .env 파일에서 OPENAI_API_KEY 등 환경변수를 불러옵니다.
load_dotenv()

CSS_PATH = Path(__file__).parent / "ui" / "style.css"

with gr.Blocks(title="노동 지킴이") as demo:
    ui = build_layout()
    bind_events(ui)

if __name__ == "__main__":
    prepare_db()  # 첫 질문을 기다리지 않도록 시작할 때 문서 벡터DB를 미리 만듭니다.
    demo.launch(theme=THEME, css_paths=[CSS_PATH])
