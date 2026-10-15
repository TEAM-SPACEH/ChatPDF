# UI B 작업 규칙 — 이벤트·사용자 편의 기능 (`feature/chat-interactions`)

UI A는 **화면에 보이는 것**을 만들고, UI B는 **그 화면이 어떻게 움직이는지**를 연결합니다.
B는 A가 넘겨주는 컴포넌트 dict와 RAG 담당의 함수 사이를 잇는 역할입니다.
두 사람이 따로 작업해도 합쳤을 때 바로 동작하도록, 이 문서의 약속(특히 [컴포넌트 key 목록](#3-컴포넌트-key-목록-ab-약속))을 지켜주세요.

> 📌 **기능 명세 (변경):** 사용자가 채팅으로 노동관련법을 질문하면 RAG로 답하는 챗봇입니다. PDF 업로드·API 키 입력 화면은 **없습니다.**
> 벡터DB는 RAG 담당의 `preprocessing.py`가 미리 만들어 둔 `chroma_db/`(컬렉션 `labor_laws`)를 앱 시작 시 한 번 불러와 쓰고, API 키는 `.env`(Spaces에서는 Secrets)의 `OPENAI_API_KEY`를 씁니다.

> A 쪽 규칙은 `docs/ui-layout-rules.md`에 있습니다. 두 문서의 key 목록은 항상 같아야 합니다.

## 1. 담당 범위

| 구분 | 파일 |
| --- | --- |
| ✅ 수정하는 파일 | `ui/events.py`, `ui/chat_actions.py` (`app.py`의 `prepare_db()` 호출 한 줄 포함) |
| ❌ 수정하지 않는 파일 | `app.py`, `ui/layout.py`, `ui/style.css`, `rag/` |

B가 하는 일:

- `.click()`, `.submit()` 이벤트 연결
- 앱 시작 시 저장된 벡터DB(`chroma_db/`) 한 번 불러오기 (`prepare_db`)
- 답변 스트리밍(`yield`)을 채팅창에 반영
- 추천 질문 버튼 클릭 시 질문 자동 전송
- 대화 초기화
- 답변 생성 중 로딩 표시와 오류 처리

B가 하지 않는 일 (A 또는 RAG 담당):

- 컴포넌트 생성, 배치, 문구, CSS → A
- 청킹, 임베딩, 검색, 프롬프트 수정 → RAG 담당

## 2. 파일 역할

| 파일 | 역할 |
| --- | --- |
| `ui/events.py` | `bind_events(ui)` 하나만 둡니다. 컴포넌트에 이벤트를 연결합니다. 로직은 넣지 않습니다. |
| `ui/chat_actions.py` | 이벤트가 호출하는 핸들러 함수와 벡터DB 준비(`prepare_db`)를 둡니다. RAG 결과를 화면용 데이터로 가공합니다. |

- RAG 기능은 `rag.answer_chain`의 `answer`만 import해서 씁니다. 그 밖의 RAG 내부 코드를 직접 가져다 쓰지 않습니다.
- 핸들러 이름은 `on_<동작>` 형식으로 짓습니다: `on_ask`, `on_clear`

## 3. 컴포넌트 key 목록 (A↔B 약속)

A의 `build_layout()`은 아래 key를 **빠짐없이, 이 이름 그대로** 반환합니다. B는 이 이름으로만 컴포넌트에 접근합니다 (`ui["chatbot"]`).

| key | 컴포넌트 | 용도 | B가 하는 일 |
| --- | --- | --- | --- |
| `chatbot` | `gr.Chatbot` | 대화 표시 | 질문·답변 메시지 추가, 스트리밍 반영 |
| `question` | `gr.Textbox` | 질문 입력 | `.submit()`으로 전송 |
| `ask_btn` | `gr.Button` | 질문하기 | `.click()`으로 전송 |
| `clear_btn` | `gr.Button` | 대화 초기화 | `.click()`으로 채팅·상태 비우기 |
| `example_btns` | `list[gr.Button]` | 추천 질문 버튼들 | 각 버튼 `.click()`으로 질문 자동 전송 |

정해둔 세부 사항:

- 기존 `output`(`gr.Markdown`)은 `chatbot`(`gr.Chatbot`)으로 **대체**되었습니다.
- 기존 `openai_key`, `pdf_file`, `status`는 기능 명세 변경으로 **삭제**되었습니다.
- `example_btns`는 버튼 **리스트**이므로 반복문으로 각 버튼에 이벤트를 겁니다.
- 컴포넌트가 더 필요하면 직접 만들지 않고 A에게 요청합니다 ([7번](#7-key를-바꾸거나-추가하고-싶을-때) 참고).

## 4. 상태 관리 규칙

| 상태 | 어디에 두나 | 설명 |
| --- | --- | --- |
| 벡터DB | `chat_actions.py` 모듈 변수 (`prepare_db()`) | 앱 전체에서 **한 번만** 만들어 모든 사용자가 같이 씁니다. 사용자별 `gr.State`를 만들지 않습니다. |
| 대화 기록 | `chatbot` 컴포넌트의 값 | 대화 기록용 `gr.State`를 따로 만들지 않습니다. 채팅창 값 하나만 기준으로 삼아서 화면과 상태가 어긋나지 않게 합니다. |

- 대화 기록은 `{"role": "user" | "assistant", "content": "..."}` 딕셔너리 리스트입니다 (Gradio 6 `gr.Chatbot` 기본 형식).
- 핸들러는 `chatbot`을 입력으로 받아 메시지를 붙인 리스트를 출력으로 돌려줍니다.

## 5. 기능별 동작 규칙

### 5-1. 벡터DB 불러오기 (`prepare_db`)

- `app.py`가 `demo.launch()` 전에 `prepare_db()`를 한 번 호출합니다.
- `chroma_db/`(환경변수 `CHROMA_DB_DIR`로 변경 가능)의 `labor_laws` 컬렉션을 `text-embedding-3-large` 임베딩으로 불러옵니다. 컬렉션 이름·임베딩 모델은 `preprocessing.py`와 **반드시 같아야** 합니다. RAG 쪽에서 바꾸면 `chat_actions.py` 상단 상수도 같이 바꿉니다.
- PDF를 읽거나 임베딩을 새로 만들지 않으므로 시작이 빠르고 비용이 들지 않습니다.
- 키가 없거나, `chroma_db/`가 없거나, 컬렉션이 비어 있으면 앱은 그대로 뜨고 질문할 때 `gr.Error`로 원인을 안내합니다. 아직 DB가 없으면 질문할 때 다시 불러오기를 시도합니다.
- PDF(`docs/노동관련법/`)와 `chroma_db/`는 저장소에 올리지 않습니다(`.gitignore`). 출처는 `docs/sources.md`에 기록합니다.

### 5-2. 질문하기 (`on_ask`)

`ask_btn.click`, `question.submit`, 추천 질문 버튼 클릭은 **모두 같은 `on_ask`** 를 호출합니다. 동작이 서로 달라지지 않게 하기 위해서입니다.

순서:

1. 사용자 메시지 `{"role": "user", "content": 질문}`을 `chatbot`에 추가합니다.
2. 답변 자리 `{"role": "assistant", "content": LOADING_TEXT}`을 추가하고 바로 `yield`합니다. (로딩 표시)
   - `LOADING_TEXT`에는 보이지 않는 표식 `<span class="judge-busy"></span>`이 들어 있습니다. 이 표식이 채팅창에 있는 동안 A의 캐릭터가 움직이므로 **지우지 마세요.** 답변·오류·빈 답변 어느 경우든 이 메시지를 덮어써야 캐릭터가 멈춥니다.
3. `answer(question, OPENAI_API_KEY, db)`(`rag/answer_chain.py`)가 `yield`하는 텍스트로 마지막 assistant 메시지의 `content`를 **덮어씁니다**. `answer()`는 조각이 아니라 **지금까지 누적된 전체 텍스트**를 돌려주므로 이어 붙이지 않습니다.
4. 출처는 `answer()`의 마지막 출력에 이미 포함되어 옵니다 ([5-5](#5-5-출처-표시)).
5. 전송 후 `question` 입력창은 비웁니다.

권장 시그니처:

```python
def on_ask(question, history):
    ...
    yield history, ""   # (chatbot, question)
```

### 5-3. 추천 질문 버튼

- 버튼에 적힌 글자(`value`)가 곧 질문입니다. 버튼 자신을 `inputs`에 넣으면 그 글자가 넘어옵니다.

```python
for btn in ui["example_btns"]:
    btn.click(on_ask, inputs=[btn, ui["chatbot"]], outputs=[ui["chatbot"], ui["question"]])
```

### 5-4. 대화 초기화 (`on_clear`)

- `chatbot`은 빈 리스트, `question`은 빈 문자열로 되돌립니다.
- 벡터DB는 **유지**합니다. 초기화 후에도 바로 다시 질문할 수 있어야 합니다.

### 5-5. 출처 표시

- 출처는 **RAG 담당이 처리**합니다. `answer()`가 마지막 `yield`에 답변 + 출처(`---` / `**검색된 참고 문서**` / 목록)를 붙여서 돌려줍니다 (`rag/source_formatter.py`, PR #5).
- B는 `answer()`가 준 텍스트를 그대로 채팅창에 덮어쓰기만 하므로 출처 처리 코드를 따로 두지 않습니다. 같은 기능이 두 곳에 생기지 않게 하기 위해서입니다.
- 출처 형식을 바꾸고 싶으면 RAG 담당에게 요청합니다.

### 5-6. 오류 처리

| 상황 | 처리 |
| --- | --- |
| 문서·API 키가 준비되지 않았거나 질문이 비어 있음 | `on_ask` 맨 앞에서 빈 질문과 `db is None`을 **직접 확인**하고 `gr.Error`를 냅니다. `answer()`는 제너레이터라 첫 `yield` 전까지 오류가 나지 않으므로, 기다리면 빈 말풍선이 채팅창에 남습니다. |
| 답변 생성 중 예외 (API 키 오류, 네트워크 등) | 마지막 assistant 메시지를 `⚠️ 답변 생성 중 오류가 발생했어요: <오류 내용>`으로 바꿔서 `yield`합니다. 로딩 문구가 그대로 남지 않게 합니다. |

- 오류 내용에 API 키 같은 민감 정보가 그대로 노출되지 않게 주의합니다.

## 6. 개발 중 로컬 테스트

1. `.env`에 `OPENAI_API_KEY=sk-...` 한 줄을 적습니다. (`OPENAI_API_KEY=`를 두 번 쓰지 않게 주의)
2. `docs/노동관련법/`에 PDF를 넣고 `python preprocessing.py`로 `chroma_db/`를 **한 번** 만듭니다. (다시 돌리면 청크가 중복 저장되니 `chroma_db/`를 지우고 실행)
3. `python app.py` 실행 → 터미널에 `[ChatPDF] 벡터DB 불러옴: labor_laws (N개 청크)`가 나오면 준비 완료입니다.

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

- [ ] PDF 파일과 `chroma_db/`가 커밋에 포함되지 않았다
- [ ] `ui["output"]`을 쓰는 곳이 남아 있지 않다
- [ ] 질문하기 버튼, Enter, 추천 질문 버튼이 모두 같은 `on_ask`를 쓴다
- [ ] 답변이 글자 단위로 스트리밍된다
- [ ] 초기화 후 바로 다시 질문할 수 있다
- [ ] `chroma_db/` 없음 / 빈 질문 / 잘못된 API 키에서 화면이 멈추지 않고 안내가 나온다
- [ ] 동작 화면 캡처(또는 GIF)를 PR 본문에 첨부했다
