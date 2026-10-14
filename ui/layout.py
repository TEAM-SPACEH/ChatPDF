# UI A — 화면 구성 (gr.Blocks, gr.Column, gr.Chatbot, gr.Textbox, gr.Button, gr.Row/Column)
# 컴포넌트를 만들고 dict로 돌려줍니다. RAG 이벤트 연결은 ui/events.py(UI B)에서 합니다.
# 컴포넌트 이름(key)을 바꾸면 events.py도 함께 맞춰주세요.
#
# [화면 전환] 홈 + 3개 화면을 gr.Column(visible=...)로 쌓고, 버튼 .click()으로
# 보이는 화면만 바꿉니다. 이 .click()은 RAG 로직이 아니라 "순수 화면 전환"이라
# layout.py 안에서 처리합니다. (업로드/질문 같은 RAG 이벤트는 events.py 담당)
import gradio as gr

# 자주 묻는 Q&A — (질문, 간단 답변) 쌍
FAQ_ITEMS = [
    (
        "근로계약서는 꼭 서면으로 받아야 하나요?",
        "네. 근로기준법 제17조에 따라 사용자는 임금·근로시간·휴일·연차 등 "
        "주요 근로조건을 **서면으로 명시**해 근로자에게 교부해야 합니다. "
        "구두 계약만 하고 서면을 주지 않으면 위법입니다.",
    ),
    (
        "비정규직(기간제·단시간)도 똑같이 보호받나요?",
        "네. 기간제·단시간 근로자도 근로기준법과 「기간제 및 단시간근로자 "
        "보호 등에 관한 법률」의 보호를 받습니다. 같은 일을 한다면 정규직과 "
        "**차별받지 않을 권리**가 있습니다.",
    ),
    (
        "수습 기간에는 월급을 적게 줘도 되나요?",
        "수습 3개월 이내에는 최저임금의 90%까지 지급할 수 있지만, "
        "**1년 미만 계약**이거나 **단순노무직**은 수습이어도 최저임금 100%를 "
        "모두 지급해야 합니다.",
    ),
    (
        "주휴수당은 어떤 경우에 받나요?",
        "1주 **15시간 이상** 일하고, 약속한 근무일을 모두 채웠다면 "
        "하루치 임금을 주휴수당으로 받을 수 있습니다. 비정규직도 조건을 "
        "충족하면 동일하게 적용됩니다.",
    ),
    (
        "계약 기간이 끝나면 자동으로 해고되나요?",
        "기간제 계약은 기간 만료로 종료되는 것이 원칙이지만, **2년을 초과**해 "
        "일했다면 기간의 정함이 없는 근로자(무기계약직)로 간주될 수 있습니다.",
    ),
]

# 근로기준법 요약집 (비정규직 근로계약 관련). 교육용 참고 자료입니다.
LABOR_LAW_MD = """
## ⚖️ 근로기준법 요약집 — 근로계약 핵심 조항

> 아래 내용은 이해를 돕기 위한 **요약**입니다. 실제 사건은 조문 전문과
> 전문가 상담을 함께 확인하세요.

### 제17조 — 근로조건의 명시
임금·소정근로시간·휴일(주휴일)·연차 유급휴가 등을 **서면으로 명시**하고
근로자에게 **교부**해야 합니다.

### 제43조 — 임금 지급
임금은 **통화로**, **직접**, **전액**을, **매월 1회 이상 일정한 날짜**에
지급해야 합니다. (체불 시 고용노동부에 진정 가능)

### 제50조 — 근로시간
1주 **40시간**, 1일 **8시간**(휴게시간 제외)을 초과할 수 없습니다.

### 제55조 — 휴일(주휴수당)
1주 소정근로일을 개근하면 **1주 1회 이상 유급휴일**을 보장받습니다.
(1주 15시간 이상 근무 시 주휴수당 발생)

### 제60조 — 연차 유급휴가
1년간 80% 이상 출근 시 **15일**, 1년 미만도 1개월 개근 시 **1일**이 발생합니다.

### 제23·26조 — 해고 제한과 예고
**정당한 이유 없이** 해고할 수 없고, 해고 시 **30일 전 예고** 또는
**30일분 이상의 통상임금**(해고예고수당)을 지급해야 합니다.

---

### 기간제·단시간 근로자 보호법
- **차별 금지**: 같은 일을 하는 정규직과 합리적 이유 없이 차별할 수 없습니다.
- **2년 초과 사용**: 기간제로 2년을 넘기면 **무기계약직**으로 봅니다.

---

📞 고용노동부 고객상담센터 ☎ **1350**
""".strip()


def build_layout():
    gr.Markdown("# 📄 근로계약 도우미", elem_id="app-header")

    # ───────────────────────────── 홈 화면 ─────────────────────────────
    with gr.Column(visible=True, elem_id="screen-home") as screen_home:
        gr.Markdown(
            "비정규직 근로자를 위한 근로계약 안내 서비스입니다.\n\n"
            "**아래에서 원하는 메뉴를 선택하세요.**",
            elem_id="home-intro",
        )
        with gr.Column(elem_id="home-menu"):
            go_faq = gr.Button(
                "💬 자주 묻는 Q&A", size="lg", elem_classes="nav-card"
            )
            go_law = gr.Button(
                "⚖️ 근로기준법 요약집", size="lg", elem_classes="nav-card"
            )
            go_chat = gr.Button(
                "🤖 챗봇과의 대화", size="lg", variant="primary",
                elem_classes="nav-card",
            )

    # ──────────────────────── 화면 1. 자주 묻는 Q&A ────────────────────────
    with gr.Column(visible=False, elem_id="screen-faq") as screen_faq:
        back_faq = gr.Button("← 홈으로", size="sm", elem_classes="back-btn")
        gr.Markdown("## 💬 자주 묻는 Q&A")
        for q, a in FAQ_ITEMS:
            with gr.Accordion(q, open=False, elem_classes="faq-item"):
                gr.Markdown(a)
        gr.Markdown(
            "더 궁금한 점은 **🤖 챗봇과의 대화**에서 계약서를 올리고 물어보세요."
        )

    # ─────────────────────── 화면 2. 근로기준법 요약집 ───────────────────────
    with gr.Column(visible=False, elem_id="screen-law") as screen_law:
        back_law = gr.Button("← 홈으로", size="sm", elem_classes="back-btn")
        gr.Markdown(LABOR_LAW_MD, elem_id="labor-law")

    # ──────────────────────── 화면 3. 챗봇과의 대화 ────────────────────────
    with gr.Column(visible=False, elem_id="screen-chat") as screen_chat:
        back_chat = gr.Button("← 홈으로", size="sm", elem_classes="back-btn")
        gr.Markdown("## 🤖 챗봇과의 대화")
        gr.Markdown("### 근로계약에 대해 무엇이든 물어보세요!")
        question = gr.Textbox(
            label="질문을 입력하세요",
            placeholder="예) 제 계약서에서 불리한 조항이 있나요?",
            elem_id="question",
        )
        ask_btn = gr.Button("질문하기", variant="primary", elem_id="ask-btn")
        output = gr.Markdown(elem_id="output")

    # ───────────────────────── 화면 전환 (.click) ─────────────────────────
    # 보이는 화면만 True로 바꿔 홈 ↔ 각 화면을 오갑니다.
    screens = [screen_home, screen_faq, screen_law, screen_chat]

    def _go(target):
        # target 화면만 보이게 하는 gr.update 리스트를 돌려줍니다.
        return [gr.update(visible=(s is target)) for s in screens]

    go_faq.click(lambda: _go(screen_faq), outputs=screens)
    go_law.click(lambda: _go(screen_law), outputs=screens)
    go_chat.click(lambda: _go(screen_chat), outputs=screens)
    for back in (back_faq, back_law, back_chat):
        back.click(lambda: _go(screen_home), outputs=screens)

    gr.Markdown("☕ Buy me a coffee", elem_id="footer")

    # B가 RAG 이벤트를 걸 컴포넌트만 반환합니다. (화면 전환 버튼은 넣지 않음)
    return {
        "question": question,
        "ask_btn": ask_btn,
        "output": output,
    }
