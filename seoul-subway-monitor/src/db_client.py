import requests
import json
from src.config import Config

class SupabaseClient:
    """
    Supabase 데이터베이스 연동 클라이언트 (REST API 방식)
    무거운 supabase 라이브러리 없이 requests로 직접 데이터를 저장합니다.
    """

    def __init__(self):
        self.supabase_url = Config.SUPABASE_URL
        self.supabase_key = Config.SUPABASE_KEY
        self.table_name = "realtime_subway_positions"
        
        # Supabase REST API 헤더 설정
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"  # 삽입된 데이터 반환 요청
        }

    def insert_data(self, raw_data_list):
        """
        API 원본 데이터 리스트를 DB 스키마에 맞게 변환 후 일괄 삽입(Bulk Insert)합니다.

        Args:
            raw_data_list (list): API로부터 받은 원본 데이터 리스트
        
        Returns:
            int: 삽입된 레코드 수
        """
        if not raw_data_list:
            return 0

        refined_data = []
        for item in raw_data_list:
            try:
                # 데이터 변환 로직
                is_last_train = True if str(item.get('lstcarAt')) == '1' else False
                
                record = {
                    "line_id": item.get('subwayId'),
                    "line_name": item.get('subwayNm'),
                    "station_id": item.get('statnId'),
                    "station_name": item.get('statnNm'),
                    "train_number": item.get('trainNo'),
                    "last_rec_date": item.get('lastRecptnDt'),
                    "last_rec_time": item.get('recptnDt'),
                    "direction_type": item.get('updnLine'),
                    "dest_station_id": item.get('statnTid'),
                    "dest_station_name": item.get('statnTnm'),
                    "train_status": item.get('trainSttus'),
                    "is_express": item.get('directAt'),
                    "is_last_train": is_last_train
                }
                refined_data.append(record)
            except Exception as e:
                print(f"[DB 변환 오류] {e}")
                continue

        if not refined_data:
            return 0

        try:
            # Supabase REST API 호출 (Bulk Insert)
            # URL: {SUPABASE_URL}/rest/v1/{TABLE_NAME}
            url = f"{self.supabase_url}/rest/v1/{self.table_name}"
            
            response = requests.post(url, headers=self.headers, json=refined_data)
            response.raise_for_status()
            
            inserted_rows = response.json()
            return len(inserted_rows)
            
        except requests.exceptions.HTTPError as e:
            print(f"[DB 삽입 오류] HTTP 상태 {e.response.status_code}: {e.response.text}")
            return 0
        except Exception as e:
            print(f"[DB 삽입 오류] 저장 실패: {e}")
            return 0

    def fetch_data(self, limit=1000):
        """
        저장된 데이터를 조회합니다.
        
        Args:
            limit (int): 조회할 데이터 건수 제한
            
        Returns:
            list: 조회된 데이터 리스트, 실패 시 빈 리스트
        """
        try:
            # Supabase REST API 호출 (Select)
            # 최신 데이터 순으로 조회
            url = f"{self.supabase_url}/rest/v1/{self.table_name}"
            params = {
                "select": "*",
                "order": "created_at.desc",
                "limit": str(limit)
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"[DB 조회 오류] 데이터 조회 실패: {e}")
            return []

if __name__ == "__main__":
    try:
        Config.validate()
        db = SupabaseClient()
        dummy_data = [{
            'subwayId': '1001', 'subwayNm': '1호선', 'statnId': '1001000133', 'statnNm': '서울역',
            'trainNo': '9999', 'lastRecptnDt': '20240101', 'recptnDt': '2024-01-01 12:00:00',
            'updnLine': '0', 'statnTid': '1001000100', 'statnTnm': '소요산',
            'trainSttus': '1', 'directAt': '0', 'lstcarAt': '0'
        }]
        # 테스트용 실행은 주석 처리 또는 실제 환경변수 있을 때만 수행
        pass 
    except Exception as e:
        print(f"설정 오류: {e}")
