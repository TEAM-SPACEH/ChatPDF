"""rag/answer_chain.py의 답변 마무리(출처·상담 안내) 테스트 (API 호출 없음).

    python -m unittest rag/test_answer_chain.py -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document  # noqa: E402

from rag.answer_chain import CONSULT_NOTICE, finalize_answer  # noqa: E402

DOC = Document(
    page_content="...",
    metadata={"law_name": "근로기준법", "article_no": "제26조", "source": "근로기준법.pdf", "page": 3, "page_end": 3},
)


class FinalizeAnswerTest(unittest.TestCase):
    def test_answer_gets_sources_then_notice(self):
        text = finalize_answer("30일 전에 예고해야 합니다.", [DOC])
        self.assertIn("**선별된 참고 조항**", text)
        self.assertIn("근로기준법 · 제26조", text)
        self.assertTrue(text.endswith(CONSULT_NOTICE))
        self.assertLess(text.index("선별된 참고 조항"), text.index(CONSULT_NOTICE))

    def test_refusal_has_no_sources_but_has_notice(self):
        text = finalize_answer("제공된 법률 문서에서 확인되지 않습니다.", [DOC])
        self.assertNotIn("선별된 참고 조항", text)
        self.assertTrue(text.endswith(CONSULT_NOTICE))

    def test_refusal_with_related_guidance_keeps_sources(self):
        text = finalize_answer("제공된 법률 문서에서 확인되지 않습니다.\n\n참고로 근로기준법에는 ...", [DOC])
        self.assertIn("선별된 참고 조항", text)

    def test_partial_unknown_in_middle_keeps_sources(self):
        text = finalize_answer("30일 전에 예고해야 합니다.\n세부 금액은 문서에서 확인되지 않습니다.", [DOC])
        self.assertIn("선별된 참고 조항", text)

    def test_no_documents_still_gets_notice(self):
        text = finalize_answer("관련 법률 문서를 찾지 못했습니다.")
        self.assertEqual(text, f"관련 법률 문서를 찾지 못했습니다.\n\n{CONSULT_NOTICE}")

    def test_refusal_on_out_of_scope_topic_gets_referral(self):
        text = finalize_answer("제공된 법률 문서에서 확인되지 않습니다.", [DOC], "알바도 4대 보험 가입해야 하나요?")
        self.assertIn("4insure.or.kr", text)
        self.assertNotIn("선별된 참고 조항", text)
        self.assertTrue(text.endswith(CONSULT_NOTICE))
        self.assertLess(text.index("4insure"), text.index(CONSULT_NOTICE))

    def test_specific_topic_wins_over_insurance(self):
        text = finalize_answer("제공된 법률 문서에서 확인되지 않습니다.", (), "고용보험 있으면 실업급여 얼마나 받나요?")
        self.assertIn("실업급여(구직급여)", text)
        self.assertNotIn("4insure", text)

    def test_normal_answer_has_no_referral(self):
        text = finalize_answer("가입 대상입니다.", [DOC], "4대 보험 가입해야 하나요?")
        self.assertNotIn("어디에 물어보면", text)

    def test_refusal_on_other_topic_has_no_referral(self):
        text = finalize_answer("제공된 법률 문서에서 확인되지 않습니다.", (), "올해 최저시급은 얼마인가요?")
        self.assertNotIn("어디에 물어보면", text)


if __name__ == "__main__":
    unittest.main()
