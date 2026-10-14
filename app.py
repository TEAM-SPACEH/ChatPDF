from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from ui.events import bind_events
from ui.layout import build_layout

# .env 파일에서 OPENAI_API_KEY 등 환경변수를 불러옵니다.
load_dotenv()

CSS_PATH = Path(__file__).parent / "ui" / "style.css"

with gr.Blocks(title="ChatPDF") as demo:
    ui = build_layout()
    bind_events(ui)

if __name__ == "__main__":
    demo.launch(css_paths=[CSS_PATH])
