# UI A — 화면에 나오는 문구 모음 (다국어)
# 배치는 ui/layout.py가 맡고, 이 파일은 글자만 담습니다. 문구 검수·수정은 여기서 하세요.
# 모든 문구는 언어별로 I18N에 모아 둡니다. 언어를 바꾸면 ui/events.py가 각 컴포넌트 값을
# localize(lang)로 바꿔 끼웁니다. 법 내용(faq)을 고치면 source_note의 기준일도 함께 바꿔주세요.

# 언어 선택 — 선택한 언어로 질문하면 한국어로 번역해 검색하고, 한국어 답변을 다시 선택 언어로 번역해 보여줍니다.
# (화면에 보이는 글자, LLM에 전달하는 언어 이름) 쌍입니다. value로는 영어 언어명을 씁니다.
# 화면 맨 위 지구본 버튼(🌐)을 누르면 아래 목록이 펼쳐집니다.
LANGUAGE_LABEL = "언어 선택 / Language"
LANGUAGES = [
    ("한국어", "Korean"),
    ("日本語", "Japanese"),
    ("English", "English"),
    ("中文", "Chinese"),
    ("Tiếng Việt", "Vietnamese"),
]
# 기본값은 한국어 — 이때는 질문·답변 번역 없이 기존 방식 그대로 동작합니다.
DEFAULT_LANGUAGE = "Korean"

# 지구본 버튼에 쓰는 아이콘과, value(영어 언어명) → 화면 글자 매핑.
LANGUAGE_ICON = "🌐"
LANG_LABELS = {value: label for label, value in LANGUAGES}


def language_button_text(value):
    """지구본 버튼에 '🌐 현재언어'를 표시합니다."""
    return f"{LANGUAGE_ICON} {LANG_LABELS.get(value, '')}".strip()


# ──────────────────────────────────────────────────────────────────────────
# 언어별 화면 문구. 키 구성은 다섯 언어가 모두 같아야 합니다.
#   app_name, tagline, notice, chat_placeholder(2줄), judge_greeting,
#   menu(chat·villain·calc), coming_soon, home_btn, question_placeholder,
#   example_questions(3), tab_chat, tab_faq, ask_btn, clear_btn,
#   source_note, faq(5×(q,a))
# ──────────────────────────────────────────────────────────────────────────
I18N = {
    "Korean": {
        "app_name": "노동 지킴이",
        "tagline": "근로계약·임금·휴가·해고, 서명하기 전에 물어보세요.",
        "notice": (
            "법률 자문이 아닌 정보 제공용 서비스입니다. "
            "정확한 판단은 고용노동부 고객상담센터 **1350**에 문의하세요."
        ),
        "chat_placeholder": [
            "계약서 문구나 일하면서 생긴 궁금증을 평소 말투로 물어보세요.",
            "답변 아래에 근거가 된 법령과 페이지를 함께 보여드려요.",
        ],
        "judge_greeting": "궁금한 노동법, 저에게 물어보세요!",
        "menu": {
            "chat": "노동법 챗봇",
            "villain": "악덕 사업주",
            "calc": "계산기",
        },
        "coming_soon": "아직 준비 중이에요. 조금만 기다려 주세요!",
        "home_btn": "홈으로",
        "question_placeholder": "예) 수습기간에도 최저임금을 다 받아야 하나요?",
        "example_questions": [
            "주 15시간 넘게 알바하면 주휴수당 받나요?",
            "근로계약서에 꼭 들어가야 하는 내용은 뭔가요?",
            "1년 일하고 그만두면 퇴직금을 받을 수 있나요?",
        ],
        "tab_chat": "질문하기",
        "tab_faq": "자주 묻는 질문",
        "ask_btn": "질문하기",
        "clear_btn": "대화 지우기",
        "source_note": "국가법령정보센터 자료를 바탕으로 2026년 10월에 정리한 요약입니다. 실제 사례는 조문 전문을 확인하세요.",
        "faq": [
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
        ],
    },
    "Japanese": {
        "app_name": "労働ガーディアン",
        "tagline": "労働契約・賃金・休暇・解雇、署名する前に質問してください。",
        "notice": (
            "法律相談ではなく情報提供のためのサービスです。"
            "正確な判断は雇用労働部の顧客相談センター **1350** にお問い合わせください。"
            "\n\n*この回答はAIによる翻訳です。正確な内容は韓国語の原文を基準としてください。*"
        ),
        "chat_placeholder": [
            "契約書の文言や働く中で生じた疑問を、普段の言葉で質問してください。",
            "回答の下に、根拠となった法令とページも一緒に表示します。",
        ],
        "judge_greeting": "労働法のこと、私に聞いてください！",
        "menu": {
            "chat": "労働法チャットボット",
            "villain": "悪質な事業主",
            "calc": "計算機",
        },
        "coming_soon": "ただいま準備中です。もう少しお待ちください！",
        "home_btn": "ホームへ",
        "question_placeholder": "例）試用期間でも最低賃金を全額もらえますか？",
        "example_questions": [
            "週15時間を超えてバイトすると週休手当はもらえますか？",
            "労働契約書に必ず記載すべき内容は何ですか？",
            "1年働いて辞めると退職金はもらえますか？",
        ],
        "tab_chat": "質問する",
        "tab_faq": "よくある質問",
        "ask_btn": "質問",
        "clear_btn": "会話を消去",
        "source_note": "国家法令情報センターの資料をもとに2026年10月にまとめた要約です。実際のケースは条文全文をご確認ください。",
        "faq": [
            (
                "労働契約書は必ず書面で受け取る必要がありますか？",
                "はい。労働基準法第17条により、使用者は賃金・労働時間・休日・年次有給休暇などの"
                "主要な労働条件を**書面で明示**し、労働者に交付しなければなりません。"
                "口頭契約だけで書面を渡さないのは違法です。",
            ),
            (
                "非正規職（有期・短時間）も同じように保護されますか？",
                "はい。有期・短時間労働者も労働基準法と「有期及び短時間労働者の保護等に関する"
                "法律」の保護を受けます。同じ仕事をしているなら、正社員と"
                "**差別されない権利**があります。",
            ),
            (
                "試用期間中は給与を少なくしてもよいのですか？",
                "試用期間3か月以内は最低賃金の90%まで支給できますが、"
                "**1年未満の契約**または**単純労務職**の場合は、試用期間でも最低賃金の100%を"
                "全額支給しなければなりません。",
            ),
            (
                "週休手当はどのような場合にもらえますか？",
                "1週間に**15時間以上**働き、約束した勤務日をすべて満たした場合、"
                "1日分の賃金を週休手当として受け取れます。非正規職も条件を"
                "満たせば同様に適用されます。",
            ),
            (
                "契約期間が終わると自動的に解雇されますか？",
                "有期契約は期間満了で終了するのが原則ですが、**2年を超えて**"
                "働いた場合は、期間の定めのない労働者（無期契約職）とみなされることがあります。",
            ),
        ],
    },
    "English": {
        "app_name": "Labor Guardian",
        "tagline": "Employment contracts, wages, leave, dismissal — ask before you sign.",
        "notice": (
            "This service provides information, not legal advice. "
            "For an accurate assessment, contact the Ministry of Employment and Labor "
            "counseling center at **1350**."
            "\n\n*This answer is AI-translated; the Korean original is the authoritative version.*"
        ),
        "chat_placeholder": [
            "Ask about contract wording or any question that comes up at work, in your own words.",
            "Below each answer we show the laws and pages it is based on.",
        ],
        "judge_greeting": "Got a labor law question? Ask me!",
        "menu": {
            "chat": "Labor Law Chatbot",
            "villain": "Bad Employers",
            "calc": "Calculator",
        },
        "coming_soon": "Coming soon. Please hang tight!",
        "home_btn": "Home",
        "question_placeholder": "e.g., Do I get the full minimum wage even during probation?",
        "example_questions": [
            "If I work over 15 hours a week part-time, do I get weekly holiday pay?",
            "What must be included in an employment contract?",
            "If I work one year and quit, can I get severance pay?",
        ],
        "tab_chat": "Ask",
        "tab_faq": "FAQ",
        "ask_btn": "Ask",
        "clear_btn": "Clear chat",
        "source_note": "A summary compiled in October 2026 based on Korea's National Law Information Center. For actual cases, check the full text of the provisions.",
        "faq": [
            (
                "Must I receive the employment contract in writing?",
                "Yes. Under Article 17 of the Labor Standards Act, the employer must "
                "**state in writing** key working conditions such as wages, working hours, "
                "holidays, and annual leave, and give them to the worker. A verbal-only "
                "contract with no written document is illegal.",
            ),
            (
                "Are non-regular (fixed-term / part-time) workers protected the same way?",
                "Yes. Fixed-term and part-time workers are also protected by the Labor "
                "Standards Act and the Act on the Protection of Fixed-term and Part-time "
                "Workers. If they do the same work, they have the **right not to be "
                "discriminated against** compared with regular workers.",
            ),
            (
                "Can wages be lower during the probation period?",
                "Within the first 3 months of probation, up to 90% of the minimum wage may "
                "be paid. However, for **contracts shorter than one year** or "
                "**simple-labor jobs**, 100% of the minimum wage must be paid even during "
                "probation.",
            ),
            (
                "When do I receive weekly holiday pay?",
                "If you work **15 hours or more** per week and complete all the agreed "
                "workdays, you can receive one day's wage as weekly holiday pay. Non-regular "
                "workers also qualify if they meet the conditions.",
            ),
            (
                "Am I automatically dismissed when the contract term ends?",
                "A fixed-term contract ends at expiry in principle, but if you have worked "
                "**more than 2 years**, you may be regarded as a worker with no fixed term "
                "(an open-ended / permanent worker).",
            ),
        ],
    },
    "Chinese": {
        "app_name": "劳动守护者",
        "tagline": "劳动合同、工资、休假、解雇——签字前先来问问。",
        "notice": (
            "本服务仅提供信息，不构成法律咨询。"
            "如需准确判断，请拨打雇佣劳动部客户咨询中心 **1350**。"
            "\n\n*本回答为AI翻译，准确内容以韩语原文为准。*"
        ),
        "chat_placeholder": [
            "请用平时的说法，询问合同条款或工作中遇到的疑问。",
            "我们会在回答下方一并显示所依据的法规和页码。",
        ],
        "judge_greeting": "劳动法有疑问？来问我吧！",
        "menu": {
            "chat": "劳动法聊天机器人",
            "villain": "恶意雇主",
            "calc": "计算器",
        },
        "coming_soon": "正在准备中，请稍候！",
        "home_btn": "返回首页",
        "question_placeholder": "例）试用期也应全额支付最低工资吗？",
        "example_questions": [
            "每周打工超过15小时能拿到周休津贴吗？",
            "劳动合同必须包含哪些内容？",
            "工作满一年后离职能拿到退职金吗？",
        ],
        "tab_chat": "提问",
        "tab_faq": "常见问题",
        "ask_btn": "提问",
        "clear_btn": "清除对话",
        "source_note": "基于韩国国家法令信息中心资料于2026年10月整理的摘要。实际案例请查阅条文全文。",
        "faq": [
            (
                "劳动合同一定要以书面形式领取吗？",
                "是的。根据《劳动基准法》第17条，雇主必须以**书面形式明确**工资、工作时间、"
                "休息日、年假等主要劳动条件，并交付给劳动者。只有口头约定而不提供书面合同属于违法。",
            ),
            (
                "非正规职（定期·短时）也能得到同样的保护吗？",
                "是的。定期和短时劳动者同样受《劳动基准法》和《关于定期及短时劳动者保护等的法律》"
                "保护。如果从事相同工作，就有**不受歧视的权利**，待遇不应低于正式员工。",
            ),
            (
                "试用期可以少发工资吗？",
                "试用期3个月以内可支付最低工资的90%，但如果是**不满一年的合同**或"
                "**简单劳务岗位**，即使在试用期也必须全额支付100%的最低工资。",
            ),
            (
                "什么情况下能领取周休津贴？",
                "若每周工作**15小时以上**，并出勤了约定的全部工作日，就可获得相当于一天工资的"
                "周休津贴。非正规职只要满足条件同样适用。",
            ),
            (
                "合同期满后会自动被解雇吗？",
                "定期合同原则上在期满时终止，但如果工作**超过2年**，"
                "则可能被视为无固定期限劳动者（无期合同员工）。",
            ),
        ],
    },
    "Vietnamese": {
        "app_name": "Người Bảo Vệ Lao Động",
        "tagline": "Hợp đồng lao động, tiền lương, nghỉ phép, sa thải — hãy hỏi trước khi ký.",
        "notice": (
            "Đây là dịch vụ cung cấp thông tin, không phải tư vấn pháp lý. "
            "Để được đánh giá chính xác, hãy liên hệ Trung tâm tư vấn khách hàng của "
            "Bộ Lao động và Việc làm theo số **1350**."
            "\n\n*Câu trả lời này do AI dịch; nội dung chính xác lấy theo bản gốc tiếng Hàn.*"
        ),
        "chat_placeholder": [
            "Hãy hỏi về câu chữ trong hợp đồng hoặc bất kỳ thắc mắc nào khi làm việc, bằng lời nói thường ngày của bạn.",
            "Dưới mỗi câu trả lời, chúng tôi hiển thị các luật và trang làm căn cứ.",
        ],
        "judge_greeting": "Thắc mắc về luật lao động? Hãy hỏi tôi!",
        "menu": {
            "chat": "Chatbot luật lao động",
            "villain": "Chủ sử dụng lao động xấu",
            "calc": "Máy tính",
        },
        "coming_soon": "Đang chuẩn bị. Vui lòng chờ một chút!",
        "home_btn": "Trang chủ",
        "question_placeholder": "Ví dụ) Trong thời gian thử việc tôi có được nhận đủ lương tối thiểu không?",
        "example_questions": [
            "Làm thêm hơn 15 giờ mỗi tuần thì có được phụ cấp nghỉ hằng tuần không?",
            "Hợp đồng lao động bắt buộc phải có những nội dung gì?",
            "Làm việc một năm rồi nghỉ thì có được nhận trợ cấp thôi việc không?",
        ],
        "tab_chat": "Hỏi",
        "tab_faq": "Hỏi đáp",
        "ask_btn": "Hỏi",
        "clear_btn": "Xóa hội thoại",
        "source_note": "Bản tóm tắt được biên soạn vào tháng 10 năm 2026 dựa trên Trung tâm Thông tin Pháp luật Quốc gia Hàn Quốc. Với trường hợp thực tế, hãy kiểm tra toàn văn điều khoản.",
        "faq": [
            (
                "Có bắt buộc phải nhận hợp đồng lao động bằng văn bản không?",
                "Có. Theo Điều 17 Luật Tiêu chuẩn Lao động, người sử dụng lao động phải "
                "**ghi rõ bằng văn bản** các điều kiện lao động chính như tiền lương, thời giờ "
                "làm việc, ngày nghỉ, nghỉ phép năm và giao cho người lao động. Chỉ giao kết "
                "bằng miệng mà không đưa văn bản là vi phạm pháp luật.",
            ),
            (
                "Lao động phi chính thức (có thời hạn / bán thời gian) có được bảo vệ như nhau không?",
                "Có. Lao động có thời hạn và bán thời gian cũng được bảo vệ bởi Luật Tiêu chuẩn "
                "Lao động và Luật Bảo vệ người lao động có thời hạn và bán thời gian. Nếu làm "
                "cùng một công việc, họ có **quyền không bị phân biệt đối xử** so với lao động "
                "chính thức.",
            ),
            (
                "Trong thời gian thử việc có được trả lương thấp hơn không?",
                "Trong vòng 3 tháng thử việc, có thể trả tới 90% mức lương tối thiểu. Tuy nhiên, "
                "với **hợp đồng dưới một năm** hoặc **công việc lao động giản đơn**, phải trả đủ "
                "100% mức lương tối thiểu ngay cả trong thời gian thử việc.",
            ),
            (
                "Khi nào thì được nhận phụ cấp nghỉ hằng tuần?",
                "Nếu bạn làm việc **từ 15 giờ trở lên** mỗi tuần và hoàn thành tất cả các ngày "
                "làm việc đã thỏa thuận, bạn có thể nhận một ngày lương làm phụ cấp nghỉ hằng "
                "tuần. Lao động phi chính thức cũng được áp dụng nếu đáp ứng điều kiện.",
            ),
            (
                "Khi hết thời hạn hợp đồng thì có bị sa thải tự động không?",
                "Về nguyên tắc, hợp đồng có thời hạn kết thúc khi hết hạn, nhưng nếu bạn đã làm "
                "việc **quá 2 năm**, bạn có thể được coi là người lao động không xác định thời "
                "hạn (lao động hợp đồng vô thời hạn).",
            ),
        ],
    },
}


def localize(language):
    """선택한 언어의 문구 묶음을 돌려줍니다. 모르는 언어는 한국어로 되돌립니다."""
    return I18N.get(language, I18N[DEFAULT_LANGUAGE])


# 레이아웃 초기 렌더용 기본(한국어) 상수 — 기존 import 이름을 그대로 유지합니다.
_KO = I18N[DEFAULT_LANGUAGE]
APP_NAME = _KO["app_name"]
TAGLINE = _KO["tagline"]
NOTICE = _KO["notice"]
CHAT_PLACEHOLDER = _KO["chat_placeholder"]
QUESTION_PLACEHOLDER = _KO["question_placeholder"]
EXAMPLE_QUESTIONS = _KO["example_questions"]
TAB_CHAT = _KO["tab_chat"]
TAB_FAQ = _KO["tab_faq"]
ASK_BTN = _KO["ask_btn"]
CLEAR_BTN = _KO["clear_btn"]
SOURCE_NOTE = _KO["source_note"]
FAQ_ITEMS = _KO["faq"]
JUDGE_GREETING = _KO["judge_greeting"]
COMING_SOON = _KO["coming_soon"]
HOME_BTN = _KO["home_btn"]
# 홈 메뉴 — (화면 key, 버튼 글자). 화면 key는 ui/layout.py의 screens, ui/events.py와 같아야 합니다.
MENU_ITEMS = list(_KO["menu"].items())
