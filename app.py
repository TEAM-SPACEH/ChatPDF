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
ARREARS_CSS_PATH = Path(__file__).parent / "ui" / "arrears.css"  # 임금체불 사업주 조회 화면 전용
ASSETS_DIR = Path(__file__).parent / "ui" / "assets"

# Hugging Face ZeroGPU Space에서만 `spaces` 패키지가 있습니다. ZeroGPU는 @spaces.GPU 함수가 하나도 없으면
# "No @spaces.GPU function detected during startup"으로 시작을 멈추는데, 이 앱은 GPU를 쓰지 않으므로
# 아무 일도 하지 않는 함수 하나로 조건만 맞춥니다. 로컬 실행에는 영향이 없습니다.
try:
    import spaces
except ImportError:
    spaces = None

if spaces is not None:

    @spaces.GPU
    def _zerogpu_placeholder():
        pass

# 캐릭터 스프라이트처럼 CSS에서 불러오는 이미지를 브라우저에 공개합니다.
gr.set_static_paths(paths=[ASSETS_DIR])

with gr.Blocks(title=APP_NAME) as demo:
    ui = build_layout()
    bind_events(ui)

if __name__ == "__main__":
    prepare_db()  # 첫 질문을 기다리지 않도록 시작할 때 문서 벡터DB를 미리 만듭니다.
    # Hugging Face Spaces는 기본으로 SSR 모드라 style.css 선택자 앞에 ".gradio-container .contain"이 붙지 않아
    # Gradio 기본 스타일에 밀립니다(면책 고지 배경이 사라지는 등). 로컬과 같은 화면이 나오도록 SSR을 끕니다.
    demo.launch(theme=THEME, css_paths=[CSS_PATH, ARREARS_CSS_PATH], ssr_mode=False)
