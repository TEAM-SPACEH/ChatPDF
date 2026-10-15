# UI A 작업 규칙 — 화면 구성

UI A는 **화면에 보이는 것**을 만들고, UI B는 **그 화면이 어떻게 움직이는지**를 연결합니다.
두 사람이 따로 작업해도 합쳤을 때 바로 동작하도록, 이 문서의 약속(특히 [컴포넌트 key 목록](#4-컴포넌트-key-목록-ab-약속))을 지켜주세요.

> B 쪽 규칙은 `docs/ui-interactions-rules.md`에 있습니다. 두 문서의 key 목록은 항상 같아야 합니다.

## 1. 담당 범위

| 구분 | 파일 |
| --- | --- |
| ✅ 수정하는 파일 | `ui/layout.py`, `ui/content.py`, `ui/font_size.py`, `ui/style.css` |
| ❌ 수정하지 않는 파일 | `ui/events.py`, `ui/chat_actions.py`, `rag/` |

`app.py`는 테마(`THEME`)와 CSS를 `demo.launch()`에 넘기는 줄만 A와 관련 있습니다.

**A가 하는 일**
- 상단(서비스명·소개·면책 고지)과 탭 배치
- 채팅창 (`gr.Chatbot`), 질문 입력창 (`gr.Textbox`), 버튼 (`gr.Button`)
- 추천 질문 버튼, 초기화 버튼 **모양 만들기**
- 화면 문구(`ui/content.py`), 테마(`THEME`), `ui/style.css` 디자인과 반응형

**A가 하지 않는 일 (B 담당)**
- `.click()`, `.submit()` 같은 이벤트 연결
- `gr.State` 생성
- 답변 스트리밍, 로딩·오류 처리 로직

## 2. 화면 구조

```
노동 지킴이 / 한 줄 소개     글자 크기 [보통][크게][아주 크게]   ← #top-row (#app-header + #font-size)
면책 고지 · 1350                                               ← #notice (README 6-1, 항상 보이게)
[질문하기] [자주 묻는 질문] [법령 요약]                          ← gr.Tabs
 ├ 질문하기: chatbot → 추천 질문 → 입력창 + 질문하기 → 대화 지우기
 ├ 자주 묻는 질문: 아코디언 + 출처·기준일
 └ 법령 요약: 요약 Markdown + 출처·기준일
```

- 탭 전환은 Gradio가 처리하므로 화면 전환용 `.click()`을 만들지 않습니다.
- 탭 이름은 모바일(390px)에서 세 개가 한 줄에 들어가도록 짧게 둡니다. 길어지면 Gradio가 탭을 `⋯` 메뉴 안으로 숨깁니다.

## 3. 파일 역할

| 파일 | 역할 |
| --- | --- |
| `ui/layout.py` | `build_layout()`이 컴포넌트를 배치하고 **dict로 반환**합니다. 테마 `THEME`도 여기서 정의합니다. |
| `ui/content.py` | 서비스명, 안내 문구, 추천 질문, Q&A, 법령 요약 같은 **글자만** 둡니다. 문구 검수는 이 파일만 보면 됩니다. |
| `ui/font_size.py` | 글자 크기 조절(보통/크게/아주 크게). 아래 '글자 크기 조절' 참고. |
| `ui/style.css` | 색·간격·반응형, 글자 크기 단계별 값. |

`layout.py` 규칙:
- `layout.py` 안에서 `gr.Blocks()`를 새로 열지 않습니다. 이미 `app.py`에서 열려 있습니다.
- `rag/`나 `ui/events.py`, `ui/chat_actions.py`를 import하지 않습니다.
- 이벤트(`.click` 등)를 걸지 않습니다. 버튼을 만들기만 하고 dict에 담아 넘깁니다.
- 레이아웃용 컴포넌트(`gr.Row`, `gr.Tab`, 꾸밈용 `gr.Markdown`)는 dict에 넣지 않습니다. **B가 이벤트를 걸어야 하는 컴포넌트만** 넣습니다.

### 글자 크기 조절 (`ui/font_size.py`)

- **브라우저에서만** 동작합니다. `gr.HTML`의 `js_on_load`가 버튼을 누르면 `<html data-font-size="lg|xl">`을 바꾸고, 고른 값을 `localStorage`(`nodong-font-size`)에 저장합니다. 서버 이벤트가 아니라서 key 표와 `ui/events.py`에는 들어가지 않습니다.
- 실제 크기는 `ui/style.css`의 `html[data-font-size=...]` 규칙이 정합니다. Gradio 글자 변수(`--text-xs` ~ `--text-xxl`)와 `html` 글자 크기를 같은 비율(크게 ×1.15, 아주 크게 ×1.3)로 키웁니다.
- 그래서 새 스타일을 쓸 때 글자 크기는 **`rem`이나 Gradio 변수(`var(--text-md)` 등)로** 씁니다. `px`로 고정하면 글자 크기 조절을 따라오지 않습니다.

## 4. 컴포넌트 key 목록 (A↔B 약속)

`build_layout()`은 아래 key를 **빠짐없이, 이 이름 그대로** 반환합니다. B는 이 이름만 보고 이벤트를 연결합니다.

| key | 컴포넌트 | 용도 | B가 하는 일 |
| --- | --- | --- | --- |
| `chatbot` | `gr.Chatbot` | 대화 표시 | 질문·답변 메시지 추가, 스트리밍 반영 |
| `question` | `gr.Textbox` | 질문 입력 | `.submit()`으로 전송 |
| `ask_btn` | `gr.Button` | 질문하기 | `.click()`으로 전송 |
| `clear_btn` | `gr.Button` | 대화 초기화 | `.click()`으로 채팅·입력창 비우기 |
| `example_btns` | `list[gr.Button]` | 추천 질문 버튼들 | 각 버튼 `.click()`으로 질문 자동 전송 |

**정해둔 세부 사항**
- `example_btns`는 버튼 **리스트**입니다. B는 버튼에 적힌 글자(`value`)를 질문으로 사용하므로, 버튼 글자 = 실제 질문 문장으로 씁니다.
- 추천 질문 문장은 `ui/content.py`의 `EXAMPLE_QUESTIONS`에 둡니다. README의 대상 사용자 시나리오(알바·사회초년생·일용직)에 맞춰 고릅니다.
- **출처(문서명·페이지)는 별도 컴포넌트를 만들지 않습니다.** RAG의 `answer()`가 답변 끝에 붙여서 `chatbot`에 표시됩니다.
- 로딩 표시는 B가 채팅창에 넣는 문구와 Gradio 기본 로딩을 사용하므로 A가 따로 만들지 않습니다.

## 5. `gr.Chatbot` 규칙

- 메시지 형식은 `{"role": "user" | "assistant", "content": "..."}` 딕셔너리 리스트입니다 (Gradio 6 기본 형식). A는 형식 관련 옵션을 바꾸지 않습니다.
- 사용 방법 안내는 `placeholder`(`CHAT_PLACEHOLDER`)로 보여줍니다. **`value`에 초기 메시지를 넣지 않습니다.** B가 초기화할 때 빈 리스트로 되돌리기 때문입니다.
- 높이, 아바타, 복사 버튼 같은 **보이는 옵션**은 A가 자유롭게 정합니다.

## 6. key를 바꾸거나 추가하고 싶을 때

1. 혼자 바꾸지 않습니다. 먼저 B와 이야기하고 합의합니다.
2. 합의한 내용을 **양쪽 문서의 key 목록 표에 먼저 반영**하고 push합니다.
3. 그다음 코드를 수정합니다.

> key 이름이 어긋나면 앱 실행 시 `KeyError`가, 반환할 컴포넌트를 만들지 않으면 `NameError`가 납니다. 표가 항상 기준입니다.

## 7. 테마·CSS 규칙

- 콘셉트는 **계약서를 형광펜으로 검토하는 느낌**입니다. 흰 종이(`#F7F8FA`), 남색 잉크(`#1B2A41`), 노란 형광펜(`#FFE45C`) 하나만 씁니다. 형광펜은 제목과 추천 질문 hover에만 씁니다.
- 글꼴: 모든 글자를 Pretendard 하나로 씁니다(jsDelivr에서 `@import`). 제목은 굵기(800)와 크기로 강조합니다.
- 테마는 `ui/layout.py`의 `THEME`(Base 테마 + 위 색)이고, `app.py`의 `demo.launch(theme=THEME, css_paths=...)`로 적용됩니다. Gradio 6에서는 `gr.Blocks(theme=..., css=...)`를 쓰지 않습니다.
- 색은 직접 값을 쓰지 말고 Gradio 테마 변수(`var(--color-accent)`, `var(--body-text-color-subdued)`, `var(--border-color-primary)` 등)를 씁니다. 그래야 다크 모드에서도 자동으로 맞춰집니다.
- 스타일을 줄 컴포넌트에는 `elem_id`, `elem_classes`를 붙입니다.
  - `elem_id`: dict key와 같은 이름을 하이픈으로 씁니다. 예: `chatbot` → `elem_id="chatbot"`, `ask_btn` → `elem_id="ask-btn"`
  - `elem_classes`: 여러 개에 같이 적용할 때 씁니다. 예: 추천 질문 버튼 → `elem_classes="example-btn"`
- Gradio 내부 클래스(`.svelte-xxxx` 같은 자동 생성 이름)를 선택자로 쓰지 않습니다. 버전이 바뀌면 깨집니다.
- 반응형 기준은 `768px`입니다. 그보다 좁으면 추천 질문·입력창·버튼이 세로 한 줄로 쌓입니다.
- CSS는 앱을 띄울 때 한 번 읽습니다. `style.css`를 고친 뒤에는 앱을 다시 실행해야 반영됩니다.

## 8. PR 올리기 전 체크리스트

- [ ] `build_layout()`이 4번 표의 key를 모두 만들고 반환한다
- [ ] `layout.py`에 이벤트 연결이나 `gr.State`가 없다
- [ ] `python app.py`로 실행해서 화면이 뜬다
- [ ] 화면에 실제 없는 기능(예: 계약서 업로드)을 안내하는 문구가 없다
- [ ] 면책 고지와 ☎1350 안내가 항상 보인다
- [ ] 글자 크기를 '아주 크게'로 바꿔도 PC·모바일 화면이 깨지지 않는다
- [ ] PC 화면과 좁은 화면(768px 이하) 캡처를 PR 본문에 첨부했다
