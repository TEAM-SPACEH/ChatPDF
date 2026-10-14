# UI A — 화면 구성 (gr.Blocks, gr.Chatbot, gr.Textbox, gr.Button, gr.Row/Column)
# 컴포넌트를 만들고 dict로 돌려줍니다. 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
import gradio as gr


def build_layout():
    gr.Markdown("# ChatPDF\n---")

    openai_key = gr.Textbox(label="OPEN_AI_API_KEY", type="password")
    pdf_file = gr.File(
        label="PDF 파일을 올려주세요!", file_types=[".pdf"], type="filepath"
    )
    status = gr.Markdown()

    gr.Markdown("---\n## PDF에게 질문해보세요!!")
    question = gr.Textbox(label="질문을 입력하세요")
    ask_btn = gr.Button("질문하기", variant="primary")
    output = gr.Markdown()

    gr.Markdown("☕ Buy me a coffee")

    return {
        "openai_key": openai_key,
        "pdf_file": pdf_file,
        "status": status,
        "question": question,
        "ask_btn": ask_btn,
        "output": output,
    }
