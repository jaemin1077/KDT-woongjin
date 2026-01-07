-- 테이블 생성 쿼리
CREATE TABLE IF NOT EXISTS realtime_subway_positions (
    line_id VARCHAR(50) NOT NULL, -- subwayId: 지하철 호선 ID
    line_name VARCHAR(50), -- subwayNm: 지하철 호선명
    station_id VARCHAR(50), -- statnId: 지하철 역 ID
    station_name VARCHAR(50), -- statnNm: 지하철 역명
    train_number VARCHAR(50), -- trainNo: 열차 번호
    last_rec_date VARCHAR(20), -- lastRecptnDt: 최종 수신 날짜
    last_rec_time VARCHAR(20), -- recptnDt: 최종 수신 시간
    direction_type VARCHAR(10), -- updnLine: 0:상행/내선, 1:하행/외선
    dest_station_id VARCHAR(50), -- statnTid: 종착역 ID
    dest_station_name VARCHAR(50), -- statnTnm: 종착역명
    train_status VARCHAR(10), -- trainSttus: 0:진입, 1:도착, 2:출발, 3:전전역출발 등
    is_express VARCHAR(10), -- directAt: 1:급행, 0:아님, 7:특급
    is_last_train BOOLEAN, -- lstcarAt: 막차 여부 (Boolean 변환)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) -- 데이터 적재 시간
);

-- 인덱스 생성 (조회 성능 향상을 위해)
CREATE INDEX idx_realtime_subway_positions_created_at ON realtime_subway_positions(created_at);
CREATE INDEX idx_realtime_subway_positions_line_id ON realtime_subway_positions(line_id);
