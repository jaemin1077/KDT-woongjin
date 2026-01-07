import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from src.db_client import SupabaseClient

# 시각화 결과 저장 폴더
OUTPUT_IMG_DIR = "docs/images"
REPORT_FILE = "docs/delay_analysis_report.md"

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_advanced_analysis():
    print("=== 심화 열차 지연 분석 및 리포팅 시작 ===")
    ensure_dir(OUTPUT_IMG_DIR)

    # 1. 데이터 로드
    db = SupabaseClient()
    print("Fetching data from DB...")
    data = db.fetch_data(limit=50000) # 충분한 데이터 확보
    
    if not data:
        print("[Error] No data found.")
        return

    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} rows.")

    # 2. 전처리 & 체류 시간 계산
    df['timestamp'] = pd.to_datetime(df['last_rec_time'])
    
    # 그룹: 호선, 역, 열차번호, 방향
    # 최소 시간(도착) ~ 최대 시간(출발/마지막 수신) 차이 계산
    group_cols = ['line_name', 'station_name', 'train_number', 'direction_type']
    dwell_df = df.groupby(group_cols).agg(
        start_time=('timestamp', 'min'),
        end_time=('timestamp', 'max'),
        status=('train_status', 'last')
    ).reset_index()

    dwell_df['dwell_seconds'] = (dwell_df['end_time'] - dwell_df['start_time']).dt.total_seconds()
    dwell_df['dwell_minutes'] = dwell_df['dwell_seconds'] / 60

    # 노이즈 제거: 10초 미만은 그냥 통과하거나 데이터가 너무 적은 것으로 간주해 제외
    valid_dwell = dwell_df[dwell_df['dwell_seconds'] >= 10].copy()
    
    print(f"Valid dwell events: {len(valid_dwell)}")
    if valid_dwell.empty:
        print("[Info] Not enough dwell events (>10s) to analyze.")
        # 빈 리포트라도 생성
        create_report(None, None, None)
        return

    # 3. 통계적 이상치 탐지 (IQR Method)
    # 전체 데이터에 대해 IQR 계산 (호선별로 하면 좋지만 일단 전체 기준)
    Q1 = valid_dwell['dwell_minutes'].quantile(0.25)
    Q3 = valid_dwell['dwell_minutes'].quantile(0.75)
    IQR = Q3 - Q1
    threshold = Q3 + 1.5 * IQR
    
    print(f"IQR Statistics: Q1={Q1:.2f}m, Q3={Q3:.2f}m, Threshold={threshold:.2f}m")
    
    # 이상치(지연) 데이터 추출
    outliers = valid_dwell[valid_dwell['dwell_minutes'] > threshold].sort_values('dwell_minutes', ascending=False)
    
    # 4. 시각화 (Visualization)
    sns.set_theme(style="whitegrid")
    
    # 4-1. 체류 시간 히스토그램
    plt.figure(figsize=(10, 6))
    sns.histplot(data=valid_dwell, x='dwell_minutes', bins=30, kde=True, color='skyblue')
    plt.title('Dwell Time Distribution (All Lines)')
    plt.xlabel('Dwell Time (minutes)')
    plt.ylabel('Frequency')
    plt.axvline(x=threshold, color='r', linestyle='--', label=f'Threshold ({threshold:.1f}m)')
    plt.legend()
    plt.savefig(f"{OUTPUT_IMG_DIR}/dwell_dist.png")
    plt.close()

    # 4-2. 호선별 Box Plot (지연 패턴 비교)
    plt.figure(figsize=(12, 8))
    # 한글 폰트 문제로 line_name을 그대로 쓰면 깨질 수 있으나 일단 시도 (안되면 네모로 나옴)
    # 깨짐 방지를 위해 영어 매핑 or 기본 폰트 사용 고려. 
    # 여기선 빠른 확인을 위해 호선명 사용하되, 깨지면 나중에 폰트 설정 필요.
    sns.boxplot(data=valid_dwell, x='line_name', y='dwell_minutes', palette="Set3")
    plt.title('Dwell Time by Line')
    plt.xticks(rotation=45)
    plt.axhline(y=threshold, color='r', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_IMG_DIR}/line_boxplot.png")
    plt.close()

    # 5. 리포트 생성 (Markdown)
    create_report(valid_dwell, outliers, threshold)

def create_report(df, outliers, threshold):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🚇 실시간 열차 지연 분석 보고서\n\n")
        f.write(f"**분석 일시**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if df is None:
            f.write("### ⚠️ 분석 불가\n데이터가 충분하지 않아 분석을 수행할 수 없습니다.\n")
            return

        # 요약 통계
        f.write("## 1. 요약 통계 (Summary Statistics)\n")
        f.write(f"- **총 분석 대상 정차 횟수**: {len(df)}건\n")
        f.write(f"- **평균 체류 시간**: {df['dwell_minutes'].mean():.2f}분\n")
        f.write(f"- **지연 임계값 (IQR Threshold)**: {threshold:.2f}분 (이 시간 이상 정차 시 지연으로 간주)\n")
        f.write(f"- **탐지된 지연 횟수**: {len(outliers)}건\n\n")

        # 시각화 결과
        f.write("## 2. 시각화 (Visualization)\n")
        f.write("### (1) 전체 체류 시간 분포\n")
        f.write("대부분의 열차가 얼마나 역에 머무르는지 보여줍니다. 오른쪽 꼬리가 길수록 지연이 많음을 의미합니다.\n\n")
        f.write("![Dwell Time Dist](images/dwell_dist.png)\n\n")
        
        f.write("### (2) 호선별 지연 패턴 비교\n")
        f.write("어떤 호선이 상대적으로 정차 시간이 긴지 비교합니다.\n\n")
        f.write("![Line Boxplot](images/line_boxplot.png)\n\n")

        # 상세 데이터
        f.write("## 3. 주요 지연 발생 구간 (Top 10 Delay Hotspots)\n")
        if outliers.empty:
            f.write("✅ **특이 사항 없음**: 임계값을 초과하는 유의미한 지연이 발견되지 않았습니다.\n")
        else:
            f.write("| 순위 | 호선 | 역명 | 열차번호 | 체류시간(분) | 상태 |\n")
            f.write("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
            for i, (_, row) in enumerate(outliers.head(10).iterrows(), 1):
                f.write(f"| {i} | {row['line_name']} | {row['station_name']} | {row['train_number']} | **{row['dwell_minutes']:.2f}** | {row['status']} |\n")

    print(f"\n[Success] Report generated at: {REPORT_FILE}")

if __name__ == "__main__":
    run_advanced_analysis()
