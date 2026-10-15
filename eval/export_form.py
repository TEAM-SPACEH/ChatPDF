"""평가 질문셋을 수업 제출 양식 CSV로 내보냅니다 (API 호출 없음).

    python eval/export_form.py --before eval/results/<개선 전 폴더> --after eval/results/<개선 후 폴더>
    python eval/export_form.py --questions eval/holdout.csv --before ... --after ... --out eval/holdout_form.csv

양식 열: No, 질문, 정답 (요약), 근거 페이지, 질문 유형, 개선 전, 개선 후, 출처 일치 (개선 후), 비고
- 개선 전·후: 각 결과의 '정답 채점'(✅/△/❌)
- 출처 일치 (개선 후): 답변 출처에 핵심 조문이 있으면 O, 없으면 X, 문서에 없는 질문은 -
- 비고: 개선 후 결과의 채점 이유(틀린 경우), 없으면 질문셋의 비고
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402

FORM_COLUMNS = ["No", "질문", "정답 (요약)", "근거 페이지", "질문 유형", "개선 전", "개선 후", "출처 일치 (개선 후)", "비고"]


def load_results(result_dir):
    with open(Path(result_dir) / "results.csv", encoding="utf-8-sig", newline="") as f:
        return {r["No"]: r for r in csv.DictReader(f)}


def build_rows(questions, before, after):
    rows = []
    for q in questions:
        b, a = before.get(q["No"], {}), after.get(q["No"], {})
        match, _, _ = run_eval.judge(q, a.get("답변", "")) if a else ("", "", "")
        note = a.get("비고", "") if a.get("정답 채점", "").strip() in ("❌", "△") else q.get("비고", "")
        rows.append({
            "No": q["No"],
            "질문": q["질문"],
            "정답 (요약)": q["정답 요약"],
            "근거 페이지": q["근거 페이지"],
            "질문 유형": q["유형"],
            "개선 전": b.get("정답 채점", ""),
            "개선 후": a.get("정답 채점", ""),
            "출처 일치 (개선 후)": match,
            "비고": note,
        })
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description="평가 질문셋을 제출 양식으로 내보내기")
    parser.add_argument("--questions", default=str(run_eval.QUESTIONS_PATH))
    parser.add_argument("--before", required=True, help="개선 전 결과 폴더")
    parser.add_argument("--after", required=True, help="개선 후 결과 폴더")
    parser.add_argument("--out", default=str(run_eval.EVAL_DIR / "questions_form.csv"))
    args = parser.parse_args(argv)

    rows = build_rows(run_eval.load_questions(args.questions), load_results(args.before), load_results(args.after))
    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:  # 엑셀에서 한글이 깨지지 않게 BOM 포함
        writer = csv.DictWriter(f, fieldnames=FORM_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{args.out}: {len(rows)}개")


if __name__ == "__main__":
    main()
