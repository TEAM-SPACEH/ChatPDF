"""조회 서비스 — 화면과 데이터 출처(지금은 가상 데이터)를 분리한다.

화면은 LookupResult만 보고 결과를 그린다. 데이터를 어디서 가져오는지는 몰라도 된다.
"""

import re
from dataclasses import dataclass, field

from arrears.mock_data import MOCK_BUSINESSES

# 조회 상태
LISTED = "listed"  # 일치하는 사업장이 있고, 그 사업장의 명단 기록이 있음
NOT_LISTED = "not_listed"  # 일치하는 사업장은 있지만 명단 기록이 없음
NOT_FOUND = "not_found"  # 입력한 번호와 일치하는 사업장이 없음


@dataclass
class LookupResult:
    status: str
    business_number: str  # 사용자가 입력한 사업자등록번호(000-00-00000 모양)
    records: list = field(default_factory=list)
    is_mock: bool = True  # 가상 데이터 결과인지. 공식 API로 바꾸면 False


def normalize_business_number(text):
    """하이픈·공백을 빼고 숫자만 남긴다. 10자리가 아니면 None."""
    digits = re.sub(r"\D", "", text or "")
    return digits if len(digits) == 10 else None


def format_business_number(digits):
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


class LookupService:
    """조회 서비스의 공통 모양. 공식 API 연동 클래스도 이것을 상속해 lookup()을 구현한다."""

    is_mock = False

    def lookup(self, business_number):
        """business_number는 normalize_business_number()를 거친 숫자 10자리."""
        raise NotImplementedError


class MockLookupService(LookupService):
    """테스트용 가상 데이터에서만 찾는다. 외부로 어떤 요청도 보내지 않는다."""

    is_mock = True

    def __init__(self, businesses=MOCK_BUSINESSES):
        self._businesses = businesses

    def lookup(self, business_number):
        records = self._businesses.get(business_number)
        if records is None:
            status, records = NOT_FOUND, []
        elif records:
            status = LISTED
        else:
            status = NOT_LISTED
        return LookupResult(
            status, format_business_number(business_number), list(records), is_mock=True
        )


def get_lookup_service():
    """화면이 쓸 조회 서비스. 공식 API 명세를 확인하기 전까지는 가상 데이터만 쓴다."""
    return MockLookupService()
