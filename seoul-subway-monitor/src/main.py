import time
import schedule
from datetime import datetime
from src.config import Config
from src.api_client import SeoulSubwayClient
from src.db_client import SupabaseClient

# 모니터링할 지하철 호선 목록
TARGET_LINES = [
    "1호선", "2호선", "3호선", "4호선", "5호선", 
    "6호선", "7호선", "8호선", "9호선", 
    "경의중앙선", "수인분당선", "신분당선", "공항철도", "경춘선"
]

def job():
    """
    주기적으로 실행되는 작업 함수.
    모든 대상 호선의 실시간 위치 데이터를 수집하여 DB에 저장합니다.
    """
    print(f"\n[작업 시작] {datetime.now()}")
    
    try:
        api_client = SeoulSubwayClient()
        db_client = SupabaseClient()
        
        total_inserted = 0
        
        for line in TARGET_LINES:
            # 1. API 데이터 수집
            data = api_client.get_realtime_position(line)
            
            if not data:
                continue
                
            # 2. DB 저장
            count = db_client.insert_data(data)
            total_inserted += count
            
            print(f"- {line}: {len(data)}건 수신 -> {count}건 저장")
            
            # API 호출 간 약간의 딜레이 (부하 방지)
            time.sleep(0.5)
            
        print(f"[작업 완료] 총 {total_inserted}건 데이터 저장 완료.")
        
    except Exception as e:
        print(f"[치명적 오류] 작업 실행 중 예외 발생: {e}")

def main():
    """
    메인 실행 함수.
    설정 검증 후 스케줄러를 가동합니다.
    """
    print("=== 서울 지하철 실시간 모니터링 시스템 가동 ===")
    
    # 1. 환경 변수 검증
    try:
        Config.validate()
        print("환경 변수 설정 확인 완료.")
    except Exception as e:
        print(f"[오류] 초기 설정 실패: {e}")
        print(".env 파일을 확인하고 올바른 API 키와 URL을 입력해주세요.")
        return

    # 2. 초기 1회 실행
    job()
    
    # 3. 스케줄 설정 (1분마다 실행)
    schedule.every(1).minutes.do(job)
    
    print("스케줄러가 시작되었습니다. (주기: 1분)")
    print("Ctrl+C를 눌러 종료할 수 있습니다.")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n시스템을 종료합니다.")
            break

if __name__ == "__main__":
    main()
