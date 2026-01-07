from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TrainLog(Base):
    __tablename__ = 'train_log'

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String, nullable=False)
    line_name = Column(String)
    station_id = Column(String)
    station_name = Column(String)
    train_number = Column(String, nullable=False)
    last_received_date = Column(String)
    last_received_time = Column(DateTime)
    direction = Column(String)  # 0: Up/Inner, 1: Down/Outer
    destination_station_id = Column(String)
    destination_station_name = Column(String)
    train_status = Column(String) # 0:Entry, 1:Arrival, 2:Departure, 3:Prev Dep
    is_express = Column(String) # 1:Express, 0:No, 7:Special
    is_last_train = Column(String) # 1:Yes, 0:No
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TrainLog(train={self.train_number}, line={self.line_name}, status={self.train_status})>"
