"""임금체불 사업주 조회 모듈.

화면(ui/arrears_tab.py)은 get_lookup_service()로 받은 서비스의 lookup()만 호출한다.
지금은 테스트용 가상 데이터(arrears/mock_data.py)만 쓰는 MockLookupService 하나뿐이다.

나중에 고용24 공식 API로 바꿀 때:
  1. 공식 API 명세서에서 실제 제공 항목·이용 권한·호출 주소를 먼저 확인한다.
  2. 확인한 명세대로 LookupService를 상속한 클래스를 새로 만들고 lookup()을 구현한다.
  3. get_lookup_service()가 그 클래스를 돌려주도록 바꾼다.
인증키는 서버(파이썬) 쪽 환경변수(.env)에서만 읽는다. 브라우저로 보내는 화면 코드에는 넣지 않는다.
명세를 확인하기 전에는 API 주소나 응답 필드를 임의로 만들지 않는다.
"""
