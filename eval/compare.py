"""여러 평가 결과를 한 표로 비교합니다 (API 호출 없음).

    python eval/compare.py 개선전=eval/results/<폴더> 개선후=eval/results/<폴더> [--questions eval/holdout.csv]

정답률은 results.csv의 '정답 채점'(사람 채점)으로, 나머지는 답변 내용으로 다시 판정합니다.
'근거 페이지 적중'은 결과에 그 칸이 있으면 그대로 쓰고(개선 전 측정), 없으면 답변의 출처 목록에서 계산합니다.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402


def load(result_dir, questions):
    path = Path(result_dir) / "results.csv"
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        q = questions[r["No"]]
        r["근거 일치"], r["모름 처리"], _ = run_eval.judge(q, r["답변"])  # 같은 판정 기준으로 다시 판정
        if not r.get("근거 페이지 적중"):
            r["근거 페이지 적중"] = run_eval.page_hit(q, run_eval.cited_pages(r["답변"]))
    return rows


def _pct(value):
    return "-" if value is None else f"{value * 100:.1f}%"


def table(runs):
    stats = {name: run_eval.summarize(rows) for name, rows in runs.items()}
    names = list(runs)

    def row(label, cell):
        return f"| {label} | " + " | ".join(cell(stats[n], runs[n]) for n in names) + " |"

    def ratio(key):
        return lambda s, _: f"{_pct(s[key][0])} ({round((s[key][0] or 0) * s[key][1])}/{s[key][1]})"

    lines = [
        "| 지표 | " + " | ".join(names) + " |",
        "| --- |" + " --- |" * len(names),
        row("**정답률** (사람 채점)", lambda s, r: f"**{_pct(s['정답률'][0])}** ({sum(run_eval.GRADE_SCORES.get(x['정답 채점'].strip(), 0) for x in r):g}/{s['정답률'][1]})"),
    ]
    for t in run_eval.TYPES:
        lines.append(row(f"　{t}", lambda s, r, t=t: f"{s['유형별 점수'][t][0]:g}/{s['유형별 점수'][t][2]}" if s['유형별 점수'][t][2] else "-"))
    lines += [
        row("**출처 정확도** (답변에 표시된 출처에 핵심 조문이 있음)", ratio("근거 일치율")),
        row("근거 페이지 적중 (LLM에 넘긴 근거에 정답 페이지가 있음)", ratio("근거 페이지 적중률")),
        row("모름 처리 (문서에 없는 질문에 '확인되지 않음')", ratio("모름 처리율")),
        row("지나친 거절", lambda s, _: f"{s['지나친 거절']}건"),
        row("평균 응답 시간", lambda s, _: f"{s['평균 응답 시간']:.1f}초"),
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="평가 결과 비교표")
    parser.add_argument("runs", nargs="+", metavar="이름=결과폴더")
    parser.add_argument("--questions", default=str(run_eval.QUESTIONS_PATH))
    args = parser.parse_args(argv)
    questions = {q["No"]: q for q in run_eval.load_questions(args.questions)}
    runs = {}
    for spec in args.runs:
        name, _, path = spec.partition("=")
        runs[name] = load(path, questions)
    print(table(runs))


if __name__ == "__main__":
    main()
