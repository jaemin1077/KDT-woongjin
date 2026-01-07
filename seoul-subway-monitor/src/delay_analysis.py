import pandas as pd
from src.db_client import SupabaseClient
import sys

def analyze_delay():
    print("=== 2. 실시간 열차 지연 및 체류 시간 분석 시 ===")
    
    # 1. DB에서 최근 데이터 조회
    db = SupabaseClient()
    print("최신 데이터를 조회 중입니다...")
    
    # 최근 1시간 정도의 트렌드를 보기 위해 넉넉하게 조회 (10,000건)
    data = db.fetch_data(limit=10000)
    
    if not data:
        print("[오류] 분석할 데이터가 없습니다.")
        return

    df = pd.DataFrame(data)
    print(f"총 {len(df)}건의 데이터를 로드했습니다.")
    
    # 2. 데이터 전처리
    # 날짜/시간 변환 (last_rec_time이 문자열이므로 datetime으로 변환)
    try:
        # DB 저장 시점(created_at)이 더 정확할 수 있으나, API 원본의 수신 시간(last_rec_time)을 우선 사용
        # last_rec_time 예: "2024-01-01 12:00:00"
        df['timestamp'] = pd.to_datetime(df['last_rec_time'])
    except Exception as e:
        print(f"[오류] 날짜 형식 변환 실패: {e}")
        return

    # 3. 그룹화: 열차별 + 역별 체류 시간 계산
    # 동일 열차(train_number)가 동일 역(station_name)에서 관측된 '최초 시각'과 '최종 시각' 계산
    # 주의: 열차 번호는 하루 동안 고유하다고 가정 (자정이 지나면 바뀔 수 있음)
    
    # 분석 대상 컬럼
    group_cols = ['line_name', 'station_name', 'train_number', 'direction_type']
    
    # 그룹별 집계
    dwell_stats = df.groupby(group_cols).agg(
        arrival_time=('timestamp', 'min'),    # 해당 역에서 처음 포착된 시간
        last_seen_time=('timestamp', 'max'),  # 해당 역에서 마지막으로 포착된 시간
        status=('train_status', 'last'),      # 가장 최근 상태 코드 (0:진입, 1:도착 등)
        count=('train_number', 'count')       # 데이터 포착 횟수
    ).reset_index()

    # 4. 체류 시간(분) 계산
    dwell_stats['dwell_seconds'] = (dwell_stats['last_seen_time'] - dwell_stats['arrival_time']).dt.total_seconds()
    dwell_stats['dwell_minutes'] = dwell_stats['dwell_seconds'] / 60
    
    # 5. 지연 의심 차량 필터링 및 리포트
    # 조건 A: 체류 시간이 3분 이상 (일반적인 정차 시간 초과)
    # 조건 B: 데이터가 최소 2회 이상 포착되어야 신뢰 가능 (한 번만 찍힌 건 통과 중일 수 있음)
    
    delayed_trains = dwell_stats[
        (dwell_stats['dwell_minutes'] >= 3.0) & 
        (dwell_stats['count'] > 1)
    ].sort_values('dwell_minutes', ascending=False)
    
    print(f"\n[분석 결과] 총 {len(dwell_stats)}개 정차 이벤트 중 {len(delayed_trains)}건의 지연/장기 정차 감지됨.")
    
    if delayed_trains.empty:
        print("\n✅ 현재 3분 이상 지연되거나 장기 정차 중인 열차가 없습니다.")
    else:
        print("\n⚠️ [경고] 장기 정차(지연 의심) 열차 목록 (Top 20)")
        print(f"{'호선':<10} | {'역명':<10} | {'열차번호':<8} | {'상태':<5} | {'체류시간(분)':<10} | {'최초포착':<8}")
        print("-" * 80)
        
        # 상태 코드 매핑 (보기 쉽게)
        status_map = {'0': '진입', '1': '도착', '2': '출발', '99': '운행중'}
        
        for _, row in delayed_trains.head(20).iterrows():
            status_str = status_map.get(str(row['status']), str(row['status']))
            arrival_str = row['arrival_time'].strftime("%H:%M")
            print(f"{row['line_name']:<10} | {row['station_name']:<10} | {row['train_number']:<8} | {status_str:<5} | {row['dwell_minutes']:<10.1f} | {arrival_str:<8}")
            
    # 전체 체류 현황 저장
    output_file = "analysis_result_delay.csv"
    dwell_stats.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n전체 분석 결과(정상 포함)가 '{output_file}'에 저장되었습니다.")

if __name__ == "__main__":
    analyze_delay()
