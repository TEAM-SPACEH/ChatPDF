---
title: Team ChatPDF
emoji: 📄
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.30.0
python_version: "3.11"
app_file: app.py
pinned: false
---

# ChatPDF

## 협업 규칙

### 작업 흐름

개선 항목 1개 = 브랜치 1개 = Pull Request 1개

```bash
# 1) 최신 main 받기
git switch main
git pull

# 2) 내 작업 브랜치 만들기
git switch -c feature/source-page

# 3) 코드 수정 후 커밋 — 작은 단위로 자주
git add app.py
git commit -m "feat: 답변 아래에 출처 페이지 표시"

# 4) 원격(GitHub)에 push
git push -u origin feature/source-page
```

1. GitHub에 뜨는 **Compare & pull request** 클릭 → PR 작성
2. 팀원 1명 이상 **Review → Approve** → **Merge pull request**
3. 병합 후 정리

```bash
git switch main
git pull
git branch -d feature/source-page
```

> main 브랜치는 보호되어 있어 직접 push할 수 없습니다. 반드시 PR로 병합합니다.

### 브랜치 이름

`feature/<작업 내용>` 형식으로 짓습니다.

- 예: `feature/chunk-tuning`, `feature/source-page`, `feature/chat-ui`

### 커밋 메시지

`<접두어>: <변경 내용>` 형식으로 씁니다.

| 접두어 | 용도 | 예시 |
| --- | --- | --- |
| `feat` | 새 기능 | `feat: gr.Chatbot 대화 UI 적용` |
| `fix` | 버그 수정 | `fix: API 키 없을 때 오류 메시지 수정` |
| `docs` | 문서 | `docs: README 실행 방법 추가` |
| `refactor` | 구조 개선 | `refactor: 체인 생성 함수 분리` |
| `test` | 평가·실험 | `test: chunk_size 500 평가 결과 추가` |

### Pull Request

- 제목: `[접두어] 변경 내용` (예: `[feat] 출처 페이지 표시`)
- 본문: 무엇을 / 왜 / 어떻게 / 테스트 결과(화면 캡처)
- 다른 팀원 1명 이상이 리뷰(Approve)한 뒤 main에 병합합니다.

### 충돌(conflict)이 났을 때

```bash
git switch feature/내브랜치
git pull origin main          # main 변경사항을 내 브랜치로 가져오기
# VS Code에서 충돌 파일 열기 → Accept Current / Incoming / Both 선택 → 저장
git add app.py
git commit -m "fix: main과 충돌 해결"
git push
```

> 💡 같은 줄을 동시에 고치면 충돌이 납니다. `app.py`에서 누가 어느 함수를 맡는지 미리 나누면 충돌이 크게 줄어듭니다.

### 꼭 지킬 것

- 🔐 **API 키를 코드나 저장소에 절대 올리지 않습니다.** 커밋 이력에 남으면 삭제해도 유출됩니다. 실수로 올렸다면 즉시 OpenAI에서 키를 폐기합니다.
- PDF 파일은 저장소에 올리지 않습니다. 사용 문서의 출처는 `docs/sources.md`에 기록합니다.
- `git push --force`는 Hugging Face Space 저장소에 최초 1회만 사용합니다. GitHub(origin)에는 절대 쓰지 않습니다.
