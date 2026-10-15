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
| `ui/events.py` | 진입점은 `bind_events(ui)` 하나입니다. 컴포넌트에 이벤트를 연결합니다. 로직은 넣지 않습니다. (예외: 화면 전환용 작은 함수 `_show_screen`, [5-4](#5-4-화면-전환-홈--각-화면)) |
| `ui/chat_actions.py` | 이벤트가 호출하는 핸들러 함수와 벡터DB 준비(`prepare_db`)를 둡니다. RAG 결과를 화면용 데이터로 가공합니다. |

- RAG 기능은 `rag.answer_chain`의 `answer`와 `rag.translate`의 `translate`만 import해서 씁니다. 그 밖의 RAG 내부 코드를 직접 가져다 쓰지 않습니다.
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
| `screens` | `dict[str, gr.Column]` | 화면 4개 — key는 `"home"`, `"chat"`, `"villain"`, `"calc"` | 메뉴·홈 버튼을 누르면 하나만 보이게 전환 |
| `menu_btns` | `dict[str, gr.Button]` | 홈 메뉴 버튼 — key는 `"chat"`, `"villain"`, `"calc"` (`screens`의 key와 같음) | `.click()`으로 같은 이름의 화면으로 전환 |
| `home_btns` | `list[gr.Button]` | 각 화면 왼쪽 위 뒤로가기 아이콘 버튼들 (글자 "홈으로"는 숨기고 화면 낭독기만 읽음) | `.click()`으로 홈 화면으로 전환 |
| `lang_btn` | `gr.Button` | 맨 위 오른쪽 지구본(🌐) 버튼 (모든 화면 공통) | `.click()`으로 `language` 목록 펼치기/접기(열림 여부는 `gr.State`) |
| `language` | `gr.Radio` | 질문·답변 언어 선택(한국어·日本語·English·中文·Tiếng Việt). 처음엔 `visible=False` | `on_ask`의 입력으로 받아 질문을 한국어로·답변을 선택 언어로 번역, 선택 시 화면 문구 전체 교체 |
| `i18n` | `dict` | 언어 변경 시 글자를 바꿀 화면 문구 컴포넌트 모음 — `home_hero`, `screen_titles`(화면 key별), `notices`, `coming_soons`, `tab_chat`, `tab_faq`, `faq_accordions`, `faq_answers`, `source_note` | `language.change`에서 `localize(lang)`로 각 컴포넌트 갱신 |

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
2. 답변 자리 `{"role": "assistant", "content": _busy(t["loading"])}`을 추가하고 바로 `yield`합니다. (로딩 표시)
   - 로딩 문구는 선택한 언어로 나옵니다(`ui/content.py`의 `loading`). `_busy()`가 붙이는 보이지 않는 표식 `<span class="judge-busy"></span>`이 들어 있습니다. 이 표식이 채팅창에 있는 동안 A의 캐릭터가 움직이므로 **지우지 마세요.** 답변·오류·빈 답변 어느 경우든 이 메시지를 덮어써야 캐릭터가 멈춥니다.
3. `answer(question, OPENAI_API_KEY, db)`(`rag/answer_chain.py`)가 `yield`하는 텍스트로 마지막 assistant 메시지의 `content`를 **덮어씁니다**. `answer()`는 조각이 아니라 **지금까지 누적된 전체 텍스트**를 돌려주므로 이어 붙이지 않습니다.
4. 출처는 `answer()`의 마지막 출력에 이미 포함되어 옵니다 ([5-6](#5-6-출처-표시)).
5. 전송 후 `question` 입력창은 비웁니다.

권장 시그니처:

```python
def on_ask(question, history, language):
    ...
    yield history, ""   # (chatbot, question)
```

#### 선택 언어로 질문·답변 (`on_ask`의 언어 처리)

- `on_ask(question, history, language)`로 선택 언어 value를 함께 받습니다.
- `language`가 `Korean`(기본값)이면 번역 없이 위 순서 그대로 동작합니다.
- 그 외 언어이면:
  1. 질문을 `rag.translate`의 `translate(question, "Korean", key)`로 한국어로 번역하고, 번역된 한국어 질문을 사용자 말풍선에 함께 보여줍니다.
  2. 번역된 한국어 질문으로 `answer()`를 호출해 한국어 답변을 받습니다.
  3. 한국어 답변을 `translate(ko_answer, language, key)`로 선택 언어로 번역해 스트리밍 출력합니다.
- 각 단계는 선택 언어의 로딩 문구(`translating_question`, `loading`, `translating_answer`)를 거칩니다. 세 문구 모두 `_busy()`로 감싸서 `.judge-busy` 표식이 들어 있어 번역 중에도 캐릭터가 움직입니다. 오류는 해당 단계용 메시지로 바꿔 보여줍니다(민감정보 마스킹).
- **진행 중·오류 문구는 전부 선택 언어로** 보여줍니다. 문구는 `ui/content.py`의 `I18N[언어]`(`empty_question`, `err_*`, `no_answer`, `no_translation`, `db_error`)에 있습니다. 벡터DB 오류는 한국어일 때만 원인(운영자용)을 그대로, 다른 언어는 짧은 안내(`db_error`)로 보여줍니다.

### 5-3. 추천 질문 버튼

- 버튼에 적힌 글자(`value`)가 곧 질문입니다. 버튼 자신을 `inputs`에 넣으면 그 글자가 넘어옵니다.

```python
for btn in ui["example_btns"]:
    btn.click(on_ask, inputs=[btn, ui["chatbot"], ui["language"]], outputs=[ui["chatbot"], ui["question"]])
```

### 5-4. 화면 전환 (홈 ↔ 각 화면)

- `menu_btns`의 각 버튼은 **같은 key의 화면**을, `home_btns`의 버튼은 `"home"` 화면을 보이게 합니다.
- 출력은 `screens`의 Column 4개이고, 고른 화면만 `visible=True`, 나머지는 `False`로 돌려줍니다. 화면을 바꿔도 채팅 기록은 그대로 남습니다(숨기기만 함).
- 서버 왕복을 빠르게 하려고 `queue=False`, `show_progress="hidden"`으로 걸고, 화면이 바뀌면 맨 위로 스크롤합니다(`js`).
- 화면 전환은 상태가 없는 단순 전환이라 핸들러는 `events.py` 안의 작은 함수로 둡니다(`chat_actions.py`에 넣지 않음).

#### 지구본 언어 메뉴 (`lang_btn`, `language`)

- `lang_btn.click`은 `language`(처음 `visible=False`)의 펼침/접힘을 토글합니다. 열림 여부는 UI 전용 `gr.State(False)`로 `bind_events` 안에서 만듭니다(화면 상태라 `chat_actions.py`에 두지 않습니다).
- `language.change`는 ① 메뉴를 닫고(`visible=False`) ② 지구본 글자를 `language_button_text(value)`로 바꾸고 ③ **화면 문구 전체를 선택 언어로 교체**합니다.
- 화면 문구 교체는 `ui.content.localize(value)`가 돌려주는 언어별 문구로, 홈·메뉴·뒤로가기·화면 이름·면책 고지·준비 중·채팅·FAQ 컴포넌트를 `gr.update`(value/placeholder/label)로 바꿉니다. 판사 말풍선이 든 HTML(홈 머리, 빈 채팅창, 준비 중)은 `ui/layout.py`의 `home_hero_html`·`chat_empty_html`·`coming_soon_html`로 다시 만듭니다.
- 출력 컴포넌트 순서(`text_targets`)와 핸들러가 돌려주는 update 순서가 **반드시 같아야** 합니다.
- 서버를 거치지 않는 글자는 `.then(js=...)`로 브라우저에서 바꿉니다: 글자 크기 버튼·목록(`ui/font_size.py`의 `LANGUAGE_JS`), 브라우저 탭 제목(`_TITLE_JS`).
- 마지막으로 `on_translate_history(chatbot, language)`가 **이미 주고받은 대화 말풍선을 새 언어로 번역**합니다(`chat_actions.py`).
  - 말풍선마다 `translate()`를 부르며, 여러 개를 동시에(최대 8개) 번역합니다. OpenAI 호출이라 화면 문구보다 조금 늦게 바뀝니다.
  - 질문 말풍선의 `> 🇰🇷` 줄(`KO_QUESTION_MARK`, 검색에 쓴 한국어 질문)은 번역하지 않고 두며, 한국어로 돌아가면 본문과 겹치므로 뺍니다.
  - 답변 준비 중(로딩 표식이 있는) 말풍선은 건너뛰고, 번역에 실패한 말풍선은 원래 글자를 그대로 둡니다. 대화가 비어 있으면 아무것도 하지 않습니다(`gr.skip()`).
  - Gradio 6은 메시지 `content`를 `[{"type": "text", "text": ...}]` 목록으로 넘겨주므로 `_text_of()`로 글자만 꺼내 씁니다.

### 5-5. 대화 초기화 (`on_clear`)

- `chatbot`은 빈 리스트, `question`은 빈 문자열로 되돌립니다.
- 벡터DB는 **유지**합니다. 초기화 후에도 바로 다시 질문할 수 있어야 합니다.

### 5-6. 출처 표시

- 출처는 **RAG 담당이 처리**합니다. `answer()`가 마지막 `yield`에 답변 + 출처(`---` / `**검색된 참고 문서**` / 목록)를 붙여서 돌려줍니다 (`rag/source_formatter.py`, PR #5).
- B는 `answer()`가 준 텍스트를 그대로 채팅창에 덮어쓰기만 하므로 출처 처리 코드를 따로 두지 않습니다. 같은 기능이 두 곳에 생기지 않게 하기 위해서입니다.
- 출처 형식을 바꾸고 싶으면 RAG 담당에게 요청합니다.

### 5-7. 오류 처리

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
