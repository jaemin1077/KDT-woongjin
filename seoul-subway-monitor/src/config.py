import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """
    프로젝트 설정 관리 클래스
    환경 변수에서 API 키 및 DB 연결 정보를 로드합니다.
    """
    
    # 서울시 공공데이터 API 키
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY", "")
    
    # Supabase 설정
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # 서울시 실시간 열차 위치 API 엔드포인트 (기본 URL)
    # 실제 호출 시: http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimeStationArrival/{START_INDEX}/{END_INDEX}/{STATION_NAME}
    # 또는 실시간 위치 API: http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimePosition/{START_INDEX}/{END_INDEX}/{subwayNm}
    # 여기서는 'realtimePosition' (실시간 열차 위치) 사용을 가정합니다.
    API_BASE_URL = "http://swopenAPI.seoul.go.kr/api/subway"

    @classmethod
    def validate(cls):
        """필수 환경 변수가 설정되었는지 확인합니다."""
        if not cls.SEOUL_API_KEY:
            raise ValueError("SEOUL_API_KEY가 설정되지 않았습니다.")
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL이 설정되지 않았습니다.")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY가 설정되지 않았습니다.")
