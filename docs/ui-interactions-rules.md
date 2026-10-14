# UI B 작업 규칙 — 이벤트·사용자 편의 기능 (`feature/chat-interactions`)

UI A는 **화면에 보이는 것**을 만들고, UI B는 **그 화면이 어떻게 움직이는지**를 연결합니다.
B는 A가 넘겨주는 컴포넌트 dict와 RAG 담당의 함수 사이를 잇는 역할입니다.
두 사람이 따로 작업해도 합쳤을 때 바로 동작하도록, 이 문서의 약속(특히 [컴포넌트 key 목록](#3-컴포넌트-key-목록-ab-약속))을 지켜주세요.

> A 쪽 규칙은 `feature/chat-layout` 브랜치의 `docs/ui-layout-rules.md`에 있습니다. 두 문서의 key 목록은 항상 같아야 합니다.

## 1. 담당 범위

| 구분 | 파일 |
| --- | --- |
| ✅ 수정하는 파일 | `ui/events.py`, `ui/chat_actions.py` |
| ❌ 수정하지 않는 파일 | `app.py`, `ui/layout.py`, `ui/style.css`, `rag/` |

B가 하는 일:

- `.click()`, `.submit()`, `.upload()` 이벤트 연결
- `gr.State`로 벡터DB 상태 관리
- 답변 스트리밍(`yield`)을 채팅창에 반영
- 추천 질문 버튼 클릭 시 질문 자동 전송
- 대화 초기화
- 출처 문서명·페이지 표시
- 답변 생성 중 로딩 표시와 오류 처리

B가 하지 않는 일 (A 또는 RAG 담당):

- 컴포넌트 생성, 배치, 문구, CSS → A
- 청킹, 임베딩, 검색, 프롬프트 수정 → RAG 담당

## 2. 파일 역할

| 파일 | 역할 |
| --- | --- |
| `ui/events.py` | `bind_events(ui)` 하나만 둡니다. `gr.State`를 만들고 컴포넌트에 이벤트를 연결합니다. 로직은 넣지 않습니다. |
| `ui/chat_actions.py` | 이벤트가 호출하는 핸들러 함수를 둡니다. RAG 결과를 화면용 데이터로 가공합니다. |

- RAG 기능은 `rag.pipeline`의 `build_db`, `answer`만 import해서 씁니다. 그 밖의 RAG 내부 코드를 직접 가져다 쓰지 않습니다.
- 핸들러 이름은 `on_<동작>` 형식으로 짓습니다: `on_upload`, `on_ask`, `on_clear`

## 3. 컴포넌트 key 목록 (A↔B 약속)

A의 `build_layout()`은 아래 key를 **빠짐없이, 이 이름 그대로** 반환합니다. B는 이 이름으로만 컴포넌트에 접근합니다 (`ui["chatbot"]`).

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

정해둔 세부 사항:

- 지금 코드의 `output`(`gr.Markdown`)은 `chatbot`(`gr.Chatbot`)으로 **대체**됩니다. `events.py`에서 `ui["output"]`을 쓰는 부분은 모두 `ui["chatbot"]` 기준으로 바꿉니다.
- `example_btns`는 버튼 **리스트**이므로 반복문으로 각 버튼에 이벤트를 겁니다.
- 컴포넌트가 더 필요하면 직접 만들지 않고 A에게 요청합니다 ([7번](#7-key를-바꾸거나-추가하고-싶을-때) 참고).

## 4. 상태 관리 규칙

| 상태 | 어디에 두나 | 설명 |
| --- | --- | --- |
| 벡터DB | `gr.State` (`db_state`) | `events.py`의 `bind_events()` 안에서 만듭니다. |
| 대화 기록 | `chatbot` 컴포넌트의 값 | 대화 기록용 `gr.State`를 따로 만들지 않습니다. 채팅창 값 하나만 기준으로 삼아서 화면과 상태가 어긋나지 않게 합니다. |

- 대화 기록은 `{"role": "user" | "assistant", "content": "..."}` 딕셔너리 리스트입니다 (Gradio 6 `gr.Chatbot` 기본 형식).
- 핸들러는 `chatbot`을 입력으로 받아 메시지를 붙인 리스트를 출력으로 돌려줍니다.

## 5. 기능별 동작 규칙

### 5-1. PDF 업로드 (`on_upload`)

- `build_db(pdf_path, openai_key)`를 호출해 `db_state`와 `status`를 갱신합니다.
- 새 PDF를 올리면 이전 대화는 다른 문서에 대한 것이므로 `chatbot`을 빈 리스트로 비웁니다.

### 5-2. 질문하기 (`on_ask`)

`ask_btn.click`, `question.submit`, 추천 질문 버튼 클릭은 **모두 같은 `on_ask`** 를 호출합니다. 동작이 서로 달라지지 않게 하기 위해서입니다.

순서:

1. 사용자 메시지 `{"role": "user", "content": 질문}`을 `chatbot`에 추가합니다.
2. 답변 자리 `{"role": "assistant", "content": "⏳ 답변을 찾는 중..."}`을 추가하고 바로 `yield`합니다. (로딩 표시)
3. `answer(question, openai_key, db)`가 `yield`하는 텍스트로 마지막 assistant 메시지의 `content`를 **덮어씁니다**. `answer()`는 조각이 아니라 **지금까지 누적된 전체 텍스트**를 돌려주므로 이어 붙이지 않습니다.
4. 답변이 끝나면 출처를 붙입니다 ([5-5](#5-5-출처-표시)).
5. 전송 후 `question` 입력창은 비웁니다.

권장 시그니처:

```python
def on_ask(question, openai_key, db, history):
    ...
    yield history, ""   # (chatbot, question)
```

### 5-3. 추천 질문 버튼

- 버튼에 적힌 글자(`value`)가 곧 질문입니다. 버튼 자신을 `inputs`에 넣으면 그 글자가 넘어옵니다.

```python
for btn in ui["example_btns"]:
    btn.click(on_ask, inputs=[btn, ui["openai_key"], db_state, ui["chatbot"]], outputs=[ui["chatbot"], ui["question"]])
```

### 5-4. 대화 초기화 (`on_clear`)

- `chatbot`은 빈 리스트, `question`은 빈 문자열로 되돌립니다.
- `db_state`(업로드한 PDF)는 **유지**합니다. 초기화 후에도 같은 PDF로 바로 다시 질문할 수 있어야 합니다.

### 5-5. 출처 표시

- 출처는 별도 컴포넌트 없이 **답변 메시지 아래에 붙여서** 표시합니다.
- 표시 형식:

```text
(답변 본문)

---
📄 출처: 파일명.pdf · p.3, p.5
```

- 페이지 번호는 PyPDFLoader 메타데이터 `page`(0부터 시작)에 **+1** 해서 보여줍니다.
- 지금 `answer()`는 답변 텍스트만 돌려주고 검색된 문서 정보는 주지 않습니다. 출처에 필요한 데이터(파일명, 페이지)는 **RAG 담당에게 요청**하고, B가 `rag/`를 직접 고치지 않습니다. 데이터가 준비되기 전까지는 출처 붙이는 함수만 만들어두고 빈 값이면 출처 줄을 생략합니다.

### 5-6. 오류 처리

| 상황 | 처리 |
| --- | --- |
| PDF를 안 올렸거나 질문이 비어 있음 | `on_ask` 맨 앞에서 `db is None`, 빈 질문을 **직접 확인**하고 `gr.Error`를 냅니다. `answer()`는 제너레이터라 첫 `yield` 전까지 오류가 나지 않으므로, 기다리면 빈 말풍선이 채팅창에 남습니다. |
| 답변 생성 중 예외 (API 키 오류, 네트워크 등) | 마지막 assistant 메시지를 `⚠️ 답변 생성 중 오류가 발생했어요: <오류 내용>`으로 바꿔서 `yield`합니다. 로딩 문구가 그대로 남지 않게 합니다. |

- 오류 내용에 API 키 같은 민감 정보가 그대로 노출되지 않게 주의합니다.

## 6. 개발 중 로컬 테스트

- A의 작업(`chatbot`, `clear_btn`, `example_btns` 추가)이 머지되기 전에는 `ui["chatbot"]` 등이 없어서 `KeyError`가 납니다.
- 테스트할 때는 로컬에서만 `ui/layout.py`에 [3번 표](#3-컴포넌트-key-목록-ab-약속)대로 임시 컴포넌트를 추가해서 실행하고, **이 변경은 커밋하지 않습니다** (`git restore ui/layout.py`).

## 7. key를 바꾸거나 추가하고 싶을 때

1. 혼자 바꾸지 않습니다. 먼저 A와 이야기하고 합의합니다.
2. 합의한 내용을 **양쪽 문서의 key 목록 표에 먼저 반영**하고 push합니다.
3. 그다음 코드를 수정합니다.

> key 이름이 어긋나면 앱 실행 시 `KeyError`가 납니다. 표가 항상 기준입니다.

## 8. 브랜치·머지 순서

- 브랜치: `feature/chat-interactions` (협업 규칙은 [README](../README.md) 참고)
- 커밋 예시: `feat: 답변 스트리밍을 채팅창에 반영`, `feat: 추천 질문 클릭 시 자동 전송`, `feat: 대화 초기화 버튼 연결`
- A의 PR이 먼저 머지되어야 B의 코드가 동작합니다. A와 B의 PR은 같은 날 **A → B 순서로 연달아** 머지합니다.
- A가 머지된 뒤에는 `git pull origin main`으로 받아서 실제 화면으로 다시 확인하고 PR을 머지합니다.

## 9. PR 올리기 전 체크리스트

- [ ] `ui/events.py`, `ui/chat_actions.py` 외의 파일을 수정하지 않았다 (테스트용 `layout.py` 수정은 되돌렸다)
- [ ] `ui["output"]`을 쓰는 곳이 남아 있지 않다
- [ ] 질문하기 버튼, Enter, 추천 질문 버튼이 모두 같은 `on_ask`를 쓴다
- [ ] 답변이 글자 단위로 스트리밍된다
- [ ] 초기화 후 같은 PDF로 다시 질문할 수 있다
- [ ] PDF 없이 질문 / 빈 질문 / 잘못된 API 키에서 화면이 멈추지 않고 안내가 나온다
- [ ] 동작 화면 캡처(또는 GIF)를 PR 본문에 첨부했다
