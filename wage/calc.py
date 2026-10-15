"""최저임금 계산 모듈.

최저시급은 wage/data/minimum_wage.csv(공공데이터포털 '고용노동부_연도별 최저임금')에서 읽는다.
계산 결과는 참고용이며 법률 판단이 아니다.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "minimum_wage.csv"

WEEKS_PER_MONTH = 365 / 7 / 12   # 약 4.345주
FULL_WEEK_HOURS = 40              # 법정 주 소정근로시간 상한
DAILY_HOURS = 8                   # 법정 1일 근로시간 상한
OVERTIME_RATE = 1.5               # 연장근로 가산(5인 이상 사업장)
PROBATION_RATE = 0.9              # 수습 감액 한도


def load_minimum_wages(path=DATA_PATH):
    with open(path, encoding="utf-8") as f:
        return {int(row["연도"]): int(row["시간급"]) for row in csv.DictReader(f)}


MINIMUM_WAGES = load_minimum_wages()


def minimum_hourly(year):
    if year not in MINIMUM_WAGES:
        raise ValueError(f"{year}년 최저임금 데이터가 없습니다.")
    return MINIMUM_WAGES[year]


def weekly_holiday_hours(weekly_hours):
    """주휴시간. 주 15시간 미만이면 0."""
    if weekly_hours < 15:
        return 0
    return min(weekly_hours, FULL_WEEK_HOURS) / FULL_WEEK_HOURS * 8


def monthly_standard_hours(weekly_hours):
    """월 기준시간(주휴 포함). 주 40시간이면 고시 기준대로 209시간."""
    if weekly_hours >= FULL_WEEK_HOURS:
        return 209
    weekly = weekly_hours + weekly_holiday_hours(weekly_hours)
    return round(weekly * WEEKS_PER_MONTH, 1)


def minimum_monthly(year, weekly_hours=FULL_WEEK_HOURS):
    return round(minimum_hourly(year) * monthly_standard_hours(weekly_hours))


def weekly_holiday_pay(hourly_wage, weekly_hours):
    return round(hourly_wage * weekly_holiday_hours(weekly_hours))


@dataclass
class WageCheck:
    year: int
    minimum_hourly: int        # 적용 최저시급(수습 감액 반영)
    converted_hourly: float    # 받은 임금을 시간급으로 바꾼 값
    is_violation: bool
    shortfall_per_hour: int    # 시간당 부족액
    notes: list = field(default_factory=list)
    laws: list = field(default_factory=lambda: ["최저임금법 제6조"])


def _check(year, converted, probation, notes):
    base = minimum_hourly(year)
    applied = round(base * PROBATION_RATE) if probation else base
    if probation:
        notes.append("수습 감액(90%)은 1년 이상 계약, 수습 3개월 이내, "
                     "단순노무직이 아닌 경우에만 허용됩니다.")
    shortfall = max(0, round(applied - converted))
    return WageCheck(year, applied, round(converted, 1), shortfall > 0, shortfall, notes)


def check_hourly(year, hourly_wage, probation=False):
    return _check(year, hourly_wage, probation, [])


def check_monthly(year, monthly_wage, weekly_hours=FULL_WEEK_HOURS, probation=False):
    """월급을 월 기준시간으로 나눠 비교. monthly_wage는 최저임금 산입 대상 임금만 넣는다."""
    hours = monthly_standard_hours(weekly_hours)
    notes = [f"월 기준시간 {hours}시간(주휴 포함)으로 나눠 계산했습니다.",
             "연장·야간·휴일수당과 실비 성격의 수당은 월급에서 빼고 입력해야 합니다."]
    return _check(year, monthly_wage / hours, probation, notes)


def check_daily(year, daily_wage, daily_hours, five_or_more=True, probation=False):
    """일당 비교. 8시간 초과분은 5인 이상 사업장이면 1.5배로 환산한다."""
    regular = min(daily_hours, DAILY_HOURS)
    overtime = max(daily_hours - DAILY_HOURS, 0)
    rate = OVERTIME_RATE if five_or_more else 1
    paid_hours = regular + overtime * rate
    notes = []
    if overtime:
        if five_or_more:
            notes.append(f"8시간을 넘는 {overtime:g}시간은 연장근로 가산(1.5배)을 반영해 "
                         f"{paid_hours:g}시간분으로 계산했습니다.")
        else:
            notes.append("5인 미만 사업장은 연장근로 가산수당이 적용되지 않아 1배로 계산했습니다.")
    notes.append("주휴수당은 일당에 포함하지 않았습니다. 1주 개근하면 따로 받을 수 있습니다.")
    result = _check(year, daily_wage / paid_hours, probation, notes)
    if overtime and five_or_more:
        result.laws.append("근로기준법 제56조")
    return result


def format_result(r):
    """챗봇·요약서에 그대로 붙일 수 있는 문장."""
    lines = [
        f"- {r.year}년 적용 최저시급: {r.minimum_hourly:,}원",
        f"- 받은 임금을 시간급으로 바꾸면: {r.converted_hourly:,.0f}원",
    ]
    if r.is_violation:
        lines.append(f"- 판단: **최저임금보다 시간당 {r.shortfall_per_hour:,}원 적을 가능성이 있습니다.**")
    else:
        lines.append("- 판단: 최저임금 이상으로 보입니다.")
    lines += [f"- 참고: {n}" for n in r.notes]
    lines.append(f"- 관련 조문: {', '.join(r.laws)}")
    lines.append("\n※ 참고용 계산이며 법률 판단이 아닙니다. 정확한 판단은 고용노동부 1350에 문의하세요.")
    return "\n".join(lines)
