import requests
import json
from src.config import Config

class SeoulSubwayClient:
    """
    서울시 지하철 실시간 위치 정보 API 클라이언트
    """

    def __init__(self):
        self.api_key = Config.SEOUL_API_KEY
        self.base_url = Config.API_BASE_URL

    def get_realtime_position(self, subway_name):
        """
        특정 호선의 실시간 열차 위치 정보를 가져옵니다.

        Args:
            subway_name (str): 조회할 호선명 (예: '1호선', '2호선', '신분당선')

        Returns:
            list: 열차 위치 정보 리스트 (오류 발생 시 빈 리스트 반환)
        """
        # URL 생성: http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimePosition/0/100/{subwayNm}
        # 한 번에 최대 100개까지 조회하도록 설정
        url = f"{self.base_url}/{self.api_key}/json/realtimePosition/0/100/{subway_name}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTP 에러 확인

            data = response.json()

            # API 응답 상태 확인
            if 'realtimePositionList' in data:
                return data['realtimePositionList']
            else:
                # 데이터가 없거나 에러 메시지가 있는 경우
                if 'RESULT' in data and 'MESSAGE' in data['RESULT']:
                    print(f"[API 경고] {subway_name}: {data['RESULT']['MESSAGE']}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"[API 오류] {subway_name} 데이터 요청 실패: {e}")
            return []
        except json.JSONDecodeError:
            print(f"[API 오류] {subway_name} 응답 JSON 파싱 실패")
            return []
        except Exception as e:
            print(f"[API 오류] {subway_name} 알 수 없는 오류: {e}")
            return []

if __name__ == "__main__":
    # 테스트 코드
    try:
        Config.validate()
        client = SeoulSubwayClient()
        # 1호선 테스트
        data = client.get_realtime_position("1호선")
        print(f"1호선 데이터 수신 건수: {len(data)}")
        if data:
            print(f"첫 번째 데이터 샘플: {data[0]}")
    except Exception as e:
        print(f"설정 오류: {e}")
