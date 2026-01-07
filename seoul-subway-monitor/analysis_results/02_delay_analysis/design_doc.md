# 2. 분석 설계서: 실시간 열차 체류 시간 분포 및 지연 패턴 분석

## 1. 개요 (Overview)
본 분석은 단순한 지연(3분 이상) 적발을 넘어, 수도권 지하철의 **일반적인 체류 시간 패턴(Normal Pattern)**을 규명하고 통계적으로 유의미한 **지연 이상치(Anomaly)**를 탐지하는 것을 목표로 합니다.

## 2. 분석 방법론 (Methodology)

### 2.1 데이터 전처리 (Preprocessing)
- **노이즈 입**: API 특성상 순간적으로 수신되었다가 사라지는 데이터(체류시간 < 10초)는 통과 열차로 간주하여 제외하거나 별도 분류.
- **파생 변수 생성**: `dwell_minutes` (체류 분), `is_rush_hour` (혼잡 시간대 여부).

### 2.2 통계적 분석 기법 (Statistical Analysis)
1.  **기술 통계 (Descriptive Pattern)**: 
    - 호선별/역별 평균 체류 시간 및 표준 편차 산출.
    - 정규 분포 여부 확인.
2.  **이상치 탐지 (Outlier Detection - IQR Method)**:
    - 단순히 절대값(3분)으로 자르지 않고, **IQR(Interquartile Range)** 기법을 사용하여 데이터 분포 상 '이질적인' 장기 정차를 탐지.
    - 지연 기준: $Q3 + 1.5 * IQR$ 초과 시 '이상 지연'으로 정의.

### 2.3 시각화 전략 (Visualization)
1.  **Box Plot (상자 그림)**: 호선별 체류 시간의 산포도와 이상치(지연 열차)를 한눈에 비교.
2.  **Histogram (히스토그램)**: 전체 체류 시간의 분포 모양 확인 (Long-tail 여부).
3.  **Bar Chart (막대 그래프)**: '지연 발생 빈도'가 가장 높은 상위 10개 역 순위.

## 3. 구현 파이프라인
1.  **Data Loader**: DB에서 대량의 데이터 로드.
2.  **Analyzer**: Pandas를 활용하여 체류 시간 계산 및 IQR 이상치 판별.
3.  **Visualizer**: Matplotlib/Seaborn으로 그래프 생성 및 `output/` 폴더에 저장.
4.  **Reporter**: 분석된 수치와 그래프 이미지를 통합하여 Markdown 보고서 자동 생성.

## 4. 예상 산출물 (Deliverables)
- 시각화 이미지: `dwell_time_distribution.png`, `delay_ranking.png`
- 결과 보고서: `docs/delay_analysis_report.md` (자동 생성)
