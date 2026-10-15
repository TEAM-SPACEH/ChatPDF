"""eval/run_eval.py의 판정·지표 로직 테스트 (API 호출 없음).

    python -m unittest eval/test_run_eval.py -v
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from langchain_core.documents import Document  # noqa: E402

import run_eval  # noqa: E402
from rag.source_formatter import format_sources  # noqa: E402


def make_answer(body, docs):
    """rag/answer_chain.py가 마지막에 돌려주는 것과 같은 모양의 답변을 만듭니다."""
    return f"{body}\n\n---\n**선별된 참고 조항**\n{format_sources(docs)}"


def doc(law, article, page):
    return Document(
        page_content="...",
        metadata={"law_name": law, "article_no": article, "source": f"docs/{law}.pdf", "page": page, "page_end": page},
    )


ROW_FACT = {"No": "7", "유형": "단순 사실", "근거 조문": "근로기준법 제26조; 근로기준법 시행규칙 제4조"}
ROW_UNKNOWN = {"No": "27", "유형": "문서에 없음", "근거 조문": ""}


class ParseTest(unittest.TestCase):
    def test_parse_articles_keeps_order_and_spaces_in_law_name(self):
        self.assertEqual(
            run_eval.parse_articles("근로자퇴직급여 보장법 제8조; 근로기준법 제76조의2"),
            [("근로자퇴직급여 보장법", "제8조"), ("근로기준법", "제76조의2")],
        )

    def test_parse_articles_rejects_bad_format(self):
        with self.assertRaises(ValueError):
            run_eval.parse_articles("근로기준법17조")

    def test_parse_cited_reads_real_source_formatter_output(self):
        text = make_answer("30일 전에 예고해야 합니다.", [
            doc("근로기준법", "제26조", 3),
            doc("근로기준법 시행규칙", "제4조", 0),
        ])
        self.assertEqual(
            run_eval.parse_cited(text),
            [("근로기준법", "제26조"), ("근로기준법 시행규칙", "제4조")],
        )

    def test_unknown_phrase_in_sources_is_ignored(self):
        # 출처 목록의 '검색된 참고 문서가 없습니다' 같은 문구는 본문 판정에 쓰지 않습니다.
        text = make_answer("30일 전에 예고해야 합니다.", [])
        self.assertFalse(run_eval.is_unknown_answer(text))


class JudgeTest(unittest.TestCase):
    def test_core_article_cited_is_match(self):
        text = make_answer("30일 전에 예고해야 합니다.", [doc("근로기준법", "제26조", 3)])
        self.assertEqual(run_eval.judge(ROW_FACT, text)[:2], ("O", "-"))

    def test_only_supporting_article_cited_is_not_match(self):
        text = make_answer("예외가 있습니다.", [doc("근로기준법 시행규칙", "제4조", 0)])
        self.assertEqual(run_eval.judge(ROW_FACT, text)[0], "X")

    def test_refusing_answerable_question_is_over_refusal(self):
        text = "제공된 법률 문서에서 질문에 적용할 근거를 확인하지 못했습니다."
        self.assertEqual(run_eval.judge(ROW_FACT, text)[:2], ("X", "X"))

    def test_unknown_question_refused_is_correct(self):
        text = "제공된 법률 문서에서 확인되지 않습니다."
        self.assertEqual(run_eval.judge(ROW_UNKNOWN, text)[:2], ("-", "O"))

    def test_unknown_question_answered_is_hallucination(self):
        text = make_answer("올해 최저시급은 10,000원입니다.", [doc("최저임금법", "제5조", 0)])
        self.assertEqual(run_eval.judge(ROW_UNKNOWN, text)[:2], ("-", "X"))


class SummaryTest(unittest.TestCase):
    ROWS = [
        {"유형": "단순 사실", "근거 일치": "O", "모름 처리": "-", "첫 글자(초)": "4.0", "전체(초)": "8.0", "오류": "", "정답 채점": "✅"},
        {"유형": "비교·종합", "근거 일치": "X", "모름 처리": "X", "첫 글자(초)": "5.0", "전체(초)": "12.0", "오류": "", "정답 채점": "△"},
        {"유형": "문서에 없음", "근거 일치": "-", "모름 처리": "O", "첫 글자(초)": "2.0", "전체(초)": "4.0", "오류": "", "정답 채점": "✅"},
        {"유형": "문서에 없음", "근거 일치": "-", "모름 처리": "X", "첫 글자(초)": "", "전체(초)": "", "오류": "APIError: x", "정답 채점": ""},
    ]

    def test_metrics(self):
        s = run_eval.summarize(self.ROWS)
        self.assertEqual(s["정답률"], (2.5 / 3, 3))         # 채점한 3개만, △=0.5
        self.assertEqual(s["근거 일치율"], (0.5, 2))        # 문서에 없음 제외
        self.assertEqual(s["모름 처리율"], (0.5, 2))        # 문서에 없음 2개 중 1개
        self.assertEqual(s["지나친 거절"], 1)
        self.assertAlmostEqual(s["평균 응답 시간"], 8.0)   # 오류 행 제외
        self.assertAlmostEqual(s["10초 이내 비율"], 2 / 3)
        self.assertEqual(s["오류"], 1)
        self.assertEqual(s["유형별 점수"]["비교·종합"], (0.5, 1, 1))
        self.assertEqual(s["유형별 점수"]["문서에 없음"], (1.0, 1, 2))

    def test_markdown_lists_failures(self):
        rows = [dict(r, No=str(i), 질문=f"질문{i}", 답변="틀린 답 | 내용", 비고="검색 실패") for i, r in enumerate(self.ROWS, 1)]
        text = run_eval.summary_markdown(run_eval.summarize(rows), "test", rows)
        self.assertIn("| 2 | △ | 질문2 | 틀린 답 / 내용 | 검색 실패 | |", text)
        self.assertNotIn("| 1 | ✅", text)

    def test_markdown_marks_unmeasured_accuracy(self):
        rows = [dict(r, **{"정답 채점": ""}) for r in self.ROWS]
        text = run_eval.summary_markdown(run_eval.summarize(rows), "test")
        self.assertIn("측정 안 됨", text)
        self.assertIn("--summarize", text)


class PageHitTest(unittest.TestCase):
    def test_parse_pages_with_ranges(self):
        self.assertEqual(
            run_eval.parse_pages("근로기준법 p.12; 근로기준법 시행령 p.10~11"),
            [("근로기준법", 12), ("근로기준법 시행령", 10), ("근로기준법 시행령", 11)],
        )

    def test_cited_pages_from_real_source_formatter(self):
        d = Document(page_content="", metadata={"law_name": "근로기준법", "article_no": "제17조", "source": "x.pdf", "page": 1, "page_end": 2})
        text = make_answer("답", [d])
        self.assertEqual(run_eval.cited_pages(text), {("근로기준법", 2), ("근로기준법", 3)})

    def test_doc_pages_uses_file_name_when_no_law_name(self):
        # 개선 전 DB 조각에는 law_name이 없어서 파일명 앞부분을 법령명으로 씁니다.
        d = Document(page_content="", metadata={"source": "/x/근로기준법(법률)(제21533호)(20261008).pdf", "page": 3})
        self.assertEqual(run_eval.doc_pages([d]), {("근로기준법", 4)})

    def test_page_hit_uses_core_page(self):
        row = {"유형": "단순 사실", "근거 페이지": "근로기준법 p.4; 근로기준법 p.9"}
        self.assertEqual(run_eval.page_hit(row, {("근로기준법", 4)}), "O")
        self.assertEqual(run_eval.page_hit(row, {("근로기준법", 9)}), "X")
        self.assertEqual(run_eval.page_hit({"유형": "문서에 없음", "근거 페이지": ""}, set()), "-")


class QueryCaptureTest(unittest.TestCase):
    def test_captures_generated_queries_log(self):
        import logging
        with run_eval.QueryCapture() as capture:
            logging.getLogger(run_eval.QueryCapture.LOGGER).info("Generated queries: %s", ["유급휴일 요건", " ", "적용 제외"])
        self.assertEqual(capture.queries, ["유급휴일 요건", "적용 제외"])


class QuestionSetTest(unittest.TestCase):
    def test_question_set_shape(self):
        questions = run_eval.load_questions()
        self.assertEqual(len(questions), 30)
        counts = {t: sum(q["유형"] == t for q in questions) for t in run_eval.TYPES}
        self.assertEqual(counts, {"단순 사실": 12, "비교·종합": 9, "표현 변형": 5, "문서에 없음": 4})
        for q in questions:
            articles = run_eval.parse_articles(q["근거 조문"])
            if q["유형"] == run_eval.UNKNOWN_TYPE:
                self.assertEqual(articles, [], q["No"])
            else:
                self.assertTrue(articles, q["No"])
                self.assertTrue(q["근거 페이지"].strip(), q["No"])


if __name__ == "__main__":
    unittest.main()
