import os
import time
import requests
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base, TrainLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

API_KEY = os.getenv("API_KEY", "sample") # Default to sample if not set
BASE_URL = "http://swopenapi.seoul.go.kr/api/subway"

# List of lines to monitor
# Note: The API expects the line name in Korean for some endpoints, or ID. 
# For realtimePosition, it typically takes the line name (e.g., '1호선', '2호선').
TARGET_LINES = [
    "1호선", "2호선", "3호선", "4호선", "5호선", 
    "6호선", "7호선", "8호선", "9호선", 
    "경의중앙선", "공항철도", "분당선", "신분당선" 
]

def fetch_realtime_position(line_name: str):
    """
    Fetch real-time position for a specific line.
    URL Format: http://swopenapi.seoul.go.kr/api/subway/{KEY}/json/realtimePosition/0/100/{line_name}
    """
    # Using a large end index to get all trains (usually < 100 per line at once)
    url = f"{BASE_URL}/{API_KEY}/json/realtimePosition/0/100/{line_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "realtimePositionList" not in data:
            logger.warning(f"No data for {line_name}. Response: {data.get('RESULT', {}).get('MESSAGE', 'Unknown')}")
            return []
            
        return data["realtimePositionList"]
        
    except Exception as e:
        logger.error(f"Error fetching data for {line_name}: {e}")
        return []

def save_to_db(db: Session, data_list: list):
    count = 0
    for item in data_list:
        try:
            # parsing date/time
            rec_date = item.get("recptnDt") 
            # item['recptnDt'] format example: "2023-10-23 10:20:30"
            rec_dt_obj = datetime.strptime(rec_date, "%Y-%m-%d %H:%M:%S") if rec_date else func.now()

            log_entry = TrainLog(
                line_id=item.get("subwayId"),
                line_name=item.get("subwayNm"),
                station_id=item.get("statnId"),
                station_name=item.get("statnNm"),
                train_number=item.get("trainNo"),
                last_received_date=item.get("lastRecptnDt"),
                last_received_time=rec_dt_obj,
                direction=item.get("updnLine"),
                destination_station_id=item.get("statnTid"),
                destination_station_name=item.get("statnTnm"),
                train_status=item.get("trainSttus"),
                is_express=item.get("directAt"),
                is_last_train=item.get("lstcarAt")
            )
            db.add(log_entry)
            count += 1
        except Exception as e:
            logger.error(f"Error processing item: {item}. Error: {e}")
            
    db.commit()
    return count

def main():
    logger.info("Starting Subway Monitoring Collector...")
    
    db = SessionLocal()
    
    try:
        while True:
            total_saved = 0
            start_time = time.time()
            
            for line in TARGET_LINES:
                logger.info(f"Fetching {line}...")
                trains = fetch_realtime_position(line)
                if trains:
                    saved_count = save_to_db(db, trains)
                    total_saved += saved_count
                    logger.info(f"Saved {saved_count} records for {line}.")
                
                # Small sleep to be nice to the API? API limit is usually high but good practice
                time.sleep(0.5) 
            
            logger.info(f"Cycle completed. Total saved: {total_saved}. Sleeping for 20 seconds...")
            
            # Sleep for remainder of the interval (e.g., 20 seconds total cycle target)
            elapsed = time.time() - start_time
            sleep_time = max(0, 20 - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        logger.info("Collector stopped by user.")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
