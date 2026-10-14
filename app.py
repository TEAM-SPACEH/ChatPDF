from pathlib import Path

import gradio as gr

from ui.events import bind_events
from ui.layout import build_layout

CSS_PATH = Path(__file__).parent / "ui" / "style.css"

with gr.Blocks(title="ChatPDF") as demo:
    ui = build_layout()
    bind_events(ui)

if __name__ == "__main__":
    demo.launch(css_paths=[CSS_PATH])
