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


if __name__ == "__main__":
    unittest.main()
