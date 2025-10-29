from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
class PriceLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    metal: str; price_usd: float; timestamp: datetime
engine = create_engine('sqlite:///./metal_data.db', echo=False)
def create_db_and_tables(): SQLModel.metadata.create_all(engine)
def log_price(metal:str, price:float, ts:datetime):
    with Session(engine) as s: pl=PriceLog(metal=metal, price_usd=price, timestamp=ts); s.add(pl); s.commit()
