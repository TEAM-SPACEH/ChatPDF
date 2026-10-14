# UI A 작업 규칙 — 화면 구성 (`feature/chat-layout`)

UI A는 **화면에 보이는 것**을 만들고, UI B는 **그 화면이 어떻게 움직이는지**를 연결합니다.
두 사람이 따로 작업해도 합쳤을 때 바로 동작하도록, 이 문서의 약속(특히 [컴포넌트 key 목록](#3-컴포넌트-key-목록-ab-약속))을 지켜주세요.

## 1. 담당 범위

| 구분 | 파일 |
| --- | --- |
| ✅ 수정하는 파일 | `ui/layout.py`, `ui/style.css` |
| ❌ 수정하지 않는 파일 | `app.py`, `ui/events.py`, `ui/chat_actions.py`, `rag/` |

**A가 하는 일**
- `gr.Blocks` 안의 전체 배치 (`gr.Row`, `gr.Column`)
- 타이틀, 서비스 소개, 시작 화면 안내 문구 (`gr.Markdown`)
- 채팅창 (`gr.Chatbot`), 질문 입력창 (`gr.Textbox`), 버튼 (`gr.Button`)
- 추천 질문 버튼, 초기화 버튼 **모양 만들기**
- `ui/style.css` 디자인과 반응형

**A가 하지 않는 일 (B 담당)**
- `.click()`, `.submit()`, `.upload()` 같은 이벤트 연결
- `gr.State` 생성
- 답변 스트리밍, 출처 표시, 로딩·오류 처리 로직

## 2. `ui/layout.py` 작성 규칙

- `build_layout()` 함수 하나가 컴포넌트를 만들고 **dict로 반환**합니다. `app.py`가 이 함수를 `gr.Blocks` 안에서 호출합니다.
- `layout.py` 안에서 `gr.Blocks()`를 새로 열지 않습니다. 이미 `app.py`에서 열려 있습니다.
- `rag/`나 `ui/events.py`, `ui/chat_actions.py`를 import하지 않습니다.
- 이벤트(`.click` 등)를 걸지 않습니다. 버튼을 만들기만 하고 dict에 담아 넘깁니다.
- 레이아웃용 컴포넌트(`gr.Row`, `gr.Column`, 꾸밈용 `gr.Markdown`)는 dict에 넣지 않아도 됩니다. **B가 이벤트를 걸어야 하는 컴포넌트만** 넣습니다.

```python
def build_layout():
    with gr.Row():
        ...
    return {
        "openai_key": openai_key,
        "pdf_file": pdf_file,
        # ... 아래 key 목록 전부
    }
```

## 3. 컴포넌트 key 목록 (A↔B 약속)

`build_layout()`은 아래 key를 **빠짐없이, 이 이름 그대로** 반환합니다. B는 이 이름만 보고 이벤트를 연결합니다.

| key | 컴포넌트 | 용도 | B가 하는 일 |
| --- | --- | --- | --- |
| `openai_key` | `gr.Textbox(type="password")` | API 키 입력 | 입력값을 RAG에 전달 |
| `pdf_file` | `gr.File(file_types=[".pdf"], type="filepath")` | PDF 업로드 | `.upload()`로 벡터DB 생성 |
| `status` | `gr.Markdown` | PDF 처리 결과 문구 | 처리 결과 표시 |
| `chatbot` | `gr.Chatbot` | 대화 표시 | 질문·답변 메시지 추가, 스트리밍 반영 |
| `question` | `gr.Textbox` | 질문 입력 | `.submit()`으로 전송 |
| `ask_btn` | `gr.Button` | 질문하기 | `.click()`으로 전송 |
| `clear_btn` | `gr.Button` | 대화 초기화 | `.click()`으로 채팅·상태 비우기 |
| `example_btns` | `list[gr.Button]` | 추천 질문 버튼들 | 각 버튼 `.click()`으로 질문 자동 전송 |

**정해둔 세부 사항**
- 지금 코드의 `output`(`gr.Markdown`)은 `chatbot`(`gr.Chatbot`)으로 **대체**합니다. `output` key는 없어집니다.
- `example_btns`는 버튼 **리스트**입니다. B는 버튼에 적힌 글자(`value`)를 질문으로 사용하므로, 버튼 글자 = 실제 질문 문장으로 씁니다.
- 추천 질문 문장은 `layout.py` 위쪽에 상수로 둡니다.
  ```python
  EXAMPLE_QUESTIONS = [
      "이 문서의 핵심 내용을 요약해줘",
      "...",
  ]
  ```
- **출처(문서명·페이지)는 별도 컴포넌트를 만들지 않습니다.** B가 답변 메시지 아래에 붙여서 `chatbot`에 표시합니다.
- 로딩 표시는 Gradio 기본 로딩을 사용하므로 A가 따로 만들지 않습니다.

## 4. `gr.Chatbot` 규칙

- 메시지 형식은 `{"role": "user" | "assistant", "content": "..."}` 딕셔너리 리스트입니다 (Gradio 6 기본 형식). A는 형식 관련 옵션을 바꾸지 않습니다.
- 시작 화면 안내(서비스 소개, 사용 방법)는 `gr.Chatbot`의 `placeholder`나 위쪽 `gr.Markdown`으로 만듭니다. **`value`에 초기 메시지를 넣지 않습니다.** B가 초기화할 때 빈 리스트로 되돌리기 때문입니다.
- 높이, 아바타, 복사 버튼 같은 **보이는 옵션**은 A가 자유롭게 정합니다.

## 5. key를 바꾸거나 추가하고 싶을 때

1. 혼자 바꾸지 않습니다. 먼저 B와 이야기하고 합의합니다.
2. 합의한 내용을 **이 문서의 key 목록 표에 먼저 반영**하고 push합니다.
3. 그다음 코드를 수정합니다.

> key 이름이 어긋나면 앱 실행 시 `KeyError`가 납니다. 표가 항상 기준입니다.

## 6. CSS 규칙 (`ui/style.css`)

- CSS는 `app.py`의 `demo.launch(css_paths=...)`로 적용됩니다. Gradio 6에서는 `gr.Blocks(css=...)`를 쓰지 않습니다.
- 스타일을 줄 컴포넌트에는 `elem_id`, `elem_classes`를 붙입니다.
  - `elem_id`: dict key와 같은 이름을 하이픈으로 씁니다. 예: `chatbot` → `elem_id="chatbot"`, `ask_btn` → `elem_id="ask-btn"`
  - `elem_classes`: 여러 개에 같이 적용할 때 씁니다. 예: 추천 질문 버튼 → `elem_classes="example-btn"`
- Gradio 내부 클래스(`.svelte-xxxx` 같은 자동 생성 이름)를 선택자로 쓰지 않습니다. 버전이 바뀌면 깨집니다.
- 반응형 기준은 `768px`입니다. 그보다 좁으면 세로 한 줄로 쌓이게 합니다.
  ```css
  @media (max-width: 768px) {
    ...
  }
  ```

## 7. 브랜치·머지 순서

- 브랜치: `feature/chat-layout` (협업 규칙은 [README](../README.md) 참고)
- 커밋 예시: `feat: gr.Chatbot 채팅 화면 적용`, `feat: 추천 질문 버튼 배치`, `feat: 모바일 반응형 스타일 추가`
- `output` → `chatbot` 변경 때문에 **A의 PR만 먼저 머지하면 `ui/events.py`가 옛 key를 찾다가 앱이 멈춥니다.** A와 B의 PR은 같은 날 **A → B 순서로 연달아** 머지합니다.

## 8. PR 올리기 전 체크리스트

- [ ] `ui/layout.py`, `ui/style.css` 외의 파일을 수정하지 않았다
- [ ] `build_layout()`이 3번 표의 key를 모두 반환한다
- [ ] `layout.py`에 이벤트 연결이나 `gr.State`가 없다
- [ ] `python app.py`로 실행해서 화면이 뜬다
  - B 작업 전에는 `ui/events.py`가 옛 key `output`을 찾아서 `KeyError: 'output'`이 납니다. 화면 확인용으로 로컬에서만 `events.py`의 `ui["output"]`을 `ui["chatbot"]`으로 잠깐 바꿔 실행하고, **이 변경은 커밋하지 않습니다** (`git restore ui/events.py`).
- [ ] PC 화면과 좁은 화면(768px 이하) 캡처를 PR 본문에 첨부했다
