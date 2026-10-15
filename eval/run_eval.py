"""평가 질문셋(eval/questions.csv)으로 RAG 답변을 측정합니다.

    python eval/run_eval.py --dry-run                 # API 없이 질문셋 검사 (비용 없음)
    python eval/run_eval.py --label v3                # 전체 실행 → eval/results/<시각>-v3/
    python eval/run_eval.py --label v3 --only 1,7,27  # 일부 질문만 실행
    python eval/run_eval.py --summarize eval/results/<폴더>/results.csv
                                                      # 사람이 '정답 채점'을 채운 뒤 지표 다시 계산

자동으로 판정하는 것: 근거 일치, 모름 처리, 응답 시간.
정답 여부(✅/△/❌)는 결과 CSV의 '정답 채점' 칸에 사람이 적습니다.
"""

import argparse
import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = ROOT / "eval"
QUESTIONS_PATH = EVAL_DIR / "questions.csv"
RESULTS_DIR = EVAL_DIR / "results"

QUESTION_COLUMNS = ["No", "유형", "질문", "정답 요약", "근거 조문", "근거 페이지", "비고"]
TYPES = ["단순 사실", "비교·종합", "표현 변형", "문서에 없음"]
UNKNOWN_TYPE = "문서에 없음"

# answer()가 근거를 찾지 못했을 때 쓰는 문구 (rag/answer_chain.py, rag/prompts.py)
UNKNOWN_PHRASES = ["확인되지 않습니다", "확인하지 못했습니다", "찾지 못했습니다"]

# answer()가 마지막에 붙이는 출처 목록의 제목 (rag/answer_chain.py)
SOURCES_HEADINGS = ["**선별된 참고 조항**", "**검색된 참고 문서**"]

# README 5. 목표 성능 지표
TARGETS = {"정답률": 0.80, "근거 일치율": 0.90, "모름 처리율": 1.00, "응답 시간(초)": 10.0}

GRADE_SCORES = {"✅": 1.0, "△": 0.5, "❌": 0.0}

RESULT_COLUMNS = [
    "No", "유형", "질문", "정답 요약", "근거 조문", "답변", "인용 조문", "검색 질문",
    "근거 일치", "모름 처리", "첫 글자(초)", "전체(초)", "오류", "정답 채점", "비고",
]


# ───────────────────────────── 질문셋 읽기 ─────────────────────────────

def load_questions(path=QUESTIONS_PATH):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in QUESTION_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"questions.csv에 없는 열: {missing}")
        return [row for row in reader if (row.get("질문") or "").strip()]


def parse_articles(cell):
    """'근로기준법 제17조; 근로기준법 시행령 제8조' → [('근로기준법', '제17조'), ...] (순서 유지)."""
    articles = []
    for part in (cell or "").split(";"):
        part = part.strip()
        if not part:
            continue
        law, _, article = part.rpartition(" ")
        if not law or not article.startswith("제"):
            raise ValueError(f"근거 조문 형식이 잘못됨: '{part}' (예: '근로기준법 제17조')")
        articles.append((law, article))
    return articles


# ───────────────────────────── 답변 판정 ─────────────────────────────

def split_answer(text):
    """답변 본문과 출처 목록 부분을 나눕니다."""
    for heading in SOURCES_HEADINGS:
        if heading in text:
            body, _, sources = text.partition(heading)
            return body.rstrip().rstrip("-").rstrip(), sources
    return text, ""


def parse_cited(text):
    """출처 목록의 '- 근로기준법 · 제17조 · 파일명.pdf · p.3' 줄에서 (법령, 조문)을 뽑습니다."""
    _, sources = split_answer(text)
    cited = []
    for line in sources.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split(" · ")]
        if len(parts) >= 2 and parts[1].startswith("제"):
            pair = (parts[0], parts[1])
            if pair not in cited:
                cited.append(pair)
    return cited


def is_unknown_answer(text):
    body, _ = split_answer(text)
    return any(phrase in body for phrase in UNKNOWN_PHRASES)


def judge(row, answer_text):
    """자동 판정: 근거 일치(O/X/-), 모름 처리(O/X/-), 인용 조문 문자열."""
    cited = parse_cited(answer_text)
    cited_text = "; ".join(f"{law} {article}" for law, article in cited)

    if row["유형"] == UNKNOWN_TYPE:
        # 문서에 없는 질문은 '확인되지 않는다'고 답해야 정답입니다.
        return "-", ("O" if is_unknown_answer(answer_text) else "X"), cited_text

    expected = parse_articles(row["근거 조문"])
    # 근거 일치: 질문의 핵심 조문(근거 조문 칸의 첫 번째)이 출처에 있으면 O
    match = "O" if expected and expected[0] in cited else "X"
    # 모름 처리: 답이 있는 질문인데 '확인되지 않는다'고 하면 X (지나친 거절)
    unknown = "X" if is_unknown_answer(answer_text) else "-"
    return match, unknown, cited_text


# ───────────────────────────── 지표 계산 ─────────────────────────────

def _ratio(values, ok):
    values = [v for v in values if v in ("O", "X")]
    return (sum(v == ok for v in values) / len(values), len(values)) if values else (None, 0)


def summarize(rows):
    """결과 행들로 README 지표를 계산합니다. 정답률은 '정답 채점'이 채워진 행만 셉니다."""
    graded = [GRADE_SCORES[r["정답 채점"].strip()] for r in rows
              if r.get("정답 채점", "").strip() in GRADE_SCORES]
    match_rate, match_n = _ratio([r["근거 일치"] for r in rows if r["유형"] != UNKNOWN_TYPE], "O")
    unknown_rate, unknown_n = _ratio([r["모름 처리"] for r in rows if r["유형"] == UNKNOWN_TYPE], "O")
    over_refusals = sum(r["모름 처리"] == "X" for r in rows if r["유형"] != UNKNOWN_TYPE)
    times = [float(r["전체(초)"]) for r in rows if r.get("전체(초)") and not r.get("오류")]
    first = [float(r["첫 글자(초)"]) for r in rows if r.get("첫 글자(초)") and not r.get("오류")]

    by_type = {}
    for t in TYPES:
        scores = [GRADE_SCORES[r["정답 채점"].strip()] for r in rows
                  if r["유형"] == t and r.get("정답 채점", "").strip() in GRADE_SCORES]
        total = sum(r["유형"] == t for r in rows)
        by_type[t] = (sum(scores), len(scores), total)

    return {
        "질문 수": len(rows),
        "정답률": (sum(graded) / len(graded) if graded else None, len(graded)),
        "유형별 점수": by_type,
        "근거 일치율": (match_rate, match_n),
        "모름 처리율": (unknown_rate, unknown_n),
        "지나친 거절": over_refusals,
        "평균 응답 시간": sum(times) / len(times) if times else None,
        "최대 응답 시간": max(times) if times else None,
        "10초 이내 비율": (sum(t <= TARGETS["응답 시간(초)"] for t in times) / len(times)) if times else None,
        "평균 첫 글자 시간": sum(first) / len(first) if first else None,
        "오류": sum(bool(r.get("오류")) for r in rows),
    }


def _pct(value):
    return "-" if value is None else f"{value * 100:.1f}%"


def _sec(value):
    return "-" if value is None else f"{value:.1f}초"


def failure_rows(rows):
    """사람 채점이 ❌ 또는 △인 질문 (실패 사례 분석용)."""
    return [r for r in rows if r.get("정답 채점", "").strip() in ("❌", "△")]


def summary_markdown(stats, label, rows=()):
    acc, acc_n = stats["정답률"]
    match, match_n = stats["근거 일치율"]
    unknown, unknown_n = stats["모름 처리율"]
    avg = stats["평균 응답 시간"]

    def verdict(value, target, lower_is_better=False):
        if value is None:
            return "측정 안 됨"
        ok = value <= target if lower_is_better else value >= target
        return "✅ 달성" if ok else "❌ 미달"

    lines = [
        f"# 평가 결과 — {label}",
        "",
        f"- 실행: {datetime.now():%Y-%m-%d %H:%M}",
        f"- 질문 수: {stats['질문 수']}개 / 오류 {stats['오류']}건",
        "",
        "| 지표 | 결과 | 목표 | 판정 | 측정 기준 |",
        "| --- | --- | --- | --- | --- |",
        f"| 정답률 | {_pct(acc)} | ≥ 80% | {verdict(acc, TARGETS['정답률'])} | 사람이 채점한 {acc_n}개 (✅=1, △=0.5, ❌=0) |",
        f"| 근거 일치율 | {_pct(match)} | ≥ 90% | {verdict(match, TARGETS['근거 일치율'])} | 답이 있는 질문 {match_n}개 중 핵심 조문을 인용한 비율 |",
        f"| 모름 처리율 | {_pct(unknown)} | 100% | {verdict(unknown, TARGETS['모름 처리율'])} | 문서에 없는 질문 {unknown_n}개 중 '확인되지 않는다'고 답한 비율 |",
        f"| 응답 시간 | 평균 {_sec(avg)} / 최대 {_sec(stats['최대 응답 시간'])} | ≤ 10초 | {verdict(avg, TARGETS['응답 시간(초)'], lower_is_better=True)} | 10초 이내 {_pct(stats['10초 이내 비율'])}, 첫 글자까지 평균 {_sec(stats['평균 첫 글자 시간'])} |",
        "",
        f"- 지나친 거절(답이 있는데 '확인되지 않는다'고 한 경우): {stats['지나친 거절']}건",
        "",
        "## 유형별 점수 (사람 채점)",
        "",
        "| 유형 | 점수 | 채점한 질문 |",
        "| --- | --- | --- |",
    ]
    for t, (score, graded_n, total) in stats["유형별 점수"].items():
        if total:
            lines.append(f"| {t} | {score:g} / {graded_n} | {graded_n} / {total} |")
    lines += [
        "",
        "## 실패 사례 분석",
        "",
        "채점이 ❌·△인 질문입니다. 원인은 results.csv의 '비고'에서 가져옵니다.",
        "",
        "| No | 채점 | 질문 | 답변 요약 | 원인 추정 | 해결 시도 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    failures = failure_rows(rows)
    for r in failures:
        body = " ".join(split_answer(r.get("답변", ""))[0].split())
        short = body[:80] + ("…" if len(body) > 80 else "")
        cell = lambda v: str(v).replace("|", "/").replace("\n", " ")
        lines.append(f"| {r['No']} | {r['정답 채점']} | {cell(r['질문'])} | {cell(short)} | {cell(r.get('비고', ''))} | |")
    if not failures:
        lines.append("| | | | | | |")
    if acc is None:
        lines += ["", "> 정답률은 `results.csv`의 '정답 채점' 칸(✅/△/❌)을 채운 뒤 "
                      "`python eval/run_eval.py --summarize <results.csv>`로 다시 계산합니다."]
    return "\n".join(lines) + "\n"


# ───────────────────────────── 실행 ─────────────────────────────

class QueryCapture(logging.Handler):
    """질문 확장(MultiQueryRetriever)이 로그로 남기는 검색 질문을 받아 둡니다."""

    LOGGER = "langchain.retrievers.multi_query"

    def __init__(self):
        super().__init__(level=logging.INFO)
        self.queries = []

    def emit(self, record):
        if record.getMessage().startswith("Generated queries") and record.args:
            self.queries = [str(q).strip() for q in record.args[0] if str(q).strip()]

    def __enter__(self):
        logger = logging.getLogger(self.LOGGER)
        self._old_level = logger.level
        logger.setLevel(logging.INFO)
        logger.addHandler(self)
        return self

    def __exit__(self, *exc):
        logger = logging.getLogger(self.LOGGER)
        logger.removeHandler(self)
        logger.setLevel(self._old_level)


def dry_run(questions):
    """API 호출 없이 질문셋을 검사합니다. 근거 조문이 실제 DB 조각에 있는지도 확인합니다."""
    from collections import Counter

    print(f"질문 {len(questions)}개")
    counts = Counter(q["유형"] for q in questions)
    for t in TYPES:
        print(f"  {t}: {counts.get(t, 0)}개")
    unknown_types = set(counts) - set(TYPES)
    problems = [f"알 수 없는 유형: {sorted(unknown_types)}"] if unknown_types else []

    sys.path.insert(0, str(ROOT))
    import preprocessing  # 같은 규칙으로 조문을 나눠서, 질문셋의 근거 조문이 DB에 들어가는지 봅니다.

    *_, chunks, _ids = preprocessing.prepare_documents(preprocessing.PDF_DIR)
    pages_by_article = {}
    for doc in chunks:
        key = (doc.metadata.get("law_name"), doc.metadata.get("article_no"))
        if key[1]:
            pages = pages_by_article.setdefault(key, set())
            pages.update(range(doc.metadata["page"] + 1, doc.metadata["page_end"] + 2))

    for q in questions:
        no = q["No"]
        try:
            articles = parse_articles(q["근거 조문"])
        except ValueError as e:
            problems.append(f"#{no}: {e}")
            continue
        if q["유형"] == UNKNOWN_TYPE:
            if articles:
                problems.append(f"#{no}: '문서에 없음' 질문에 근거 조문이 적혀 있음")
            continue
        if not articles:
            problems.append(f"#{no}: 근거 조문이 비어 있음")
        for law, article in articles:
            pages = pages_by_article.get((law, article))
            if not pages:
                problems.append(f"#{no}: DB 조각에 없는 조문 — {law} {article}")
            else:
                print(f"  #{no:>2} {law} {article}: p.{min(pages)}~{max(pages)}")

    if problems:
        print("\n문제:")
        for p in problems:
            print("  -", p)
        return 1
    print("\n✅ 질문셋 이상 없음 (API 호출 없음)")
    return 0


def run(questions, label):
    sys.path.insert(0, str(ROOT))
    import ui.chat_actions as app_actions  # 앱과 같은 DB·키 설정을 씁니다.
    from rag.answer_chain import answer

    db = app_actions.prepare_db()
    if db is None:
        raise SystemExit(f"벡터DB를 불러오지 못했습니다: {app_actions._db_error}")
    key = app_actions._openai_key()

    out_dir = RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M}-{label}"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] #{q['No']} {q['질문']}")
        text, error, first_at = "", "", None
        start = time.perf_counter()
        with QueryCapture() as capture:
            try:
                for text in answer(q["질문"], key, db):
                    if first_at is None and text:
                        first_at = time.perf_counter() - start
            except Exception as e:  # 한 질문이 실패해도 나머지는 계속 측정합니다.
                error = f"{type(e).__name__}: {e}"
        total = time.perf_counter() - start

        match, unknown, cited = judge(q, text) if not error else ("X", "X", "")
        rows.append({
            "No": q["No"], "유형": q["유형"], "질문": q["질문"], "정답 요약": q["정답 요약"],
            "근거 조문": q["근거 조문"], "답변": text, "인용 조문": cited,
            "검색 질문": " | ".join(capture.queries),
            "근거 일치": match, "모름 처리": unknown,
            "첫 글자(초)": f"{first_at:.2f}" if first_at is not None else "",
            "전체(초)": f"{total:.2f}", "오류": error, "정답 채점": "", "비고": q.get("비고", ""),
        })
        print(f"    {total:.1f}초 · 근거 일치 {match} · 모름 처리 {unknown}" + (f" · 오류 {error}" if error else ""))

    write_results(rows, out_dir / "results.csv")
    (out_dir / "summary.md").write_text(summary_markdown(summarize(rows), label, rows), encoding="utf-8")
    print(f"\n결과: {out_dir}")
    print((out_dir / "summary.md").read_text(encoding="utf-8"))


def write_results(rows, path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:  # 엑셀에서 한글이 깨지지 않게 BOM 포함
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def resummarize(path):
    path = Path(path)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    label = path.parent.name
    text = summary_markdown(summarize(rows), label, rows)
    (path.parent / "summary.md").write_text(text, encoding="utf-8")
    print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="노동 지킴이 RAG 평가")
    parser.add_argument("--dry-run", action="store_true", help="API 없이 질문셋만 검사")
    parser.add_argument("--label", default="run", help="결과 폴더 이름에 붙일 이름 (예: v3, before)")
    parser.add_argument("--only", help="실행할 질문 번호 (예: 1,7,27)")
    parser.add_argument("--questions", default=str(QUESTIONS_PATH), help="질문셋 CSV 경로")
    parser.add_argument("--summarize", metavar="RESULTS_CSV", help="채점한 결과 CSV로 지표만 다시 계산")
    args = parser.parse_args(argv)

    if args.summarize:
        resummarize(args.summarize)
        return 0

    questions = load_questions(args.questions)
    if args.only:
        wanted = {n.strip() for n in args.only.split(",")}
        questions = [q for q in questions if q["No"] in wanted]

    if args.dry_run:
        return dry_run(questions)
    run(questions, args.label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
