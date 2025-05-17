from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    food_cd = Column(String, unique=True, index=True)
    group_name = Column(String)
    food_name = Column(String, index=True)
    research_year = Column(String, index=True)
    maker_name = Column(String, index=True)
    ref_name = Column(String)
    serving_size = Column(Float)
    calorie = Column(Float)
    carbohydrate = Column(Float)
    protein = Column(Float)
    province = Column(Float)  # 지방
    sugars = Column(Float)
    salt = Column(Float)
    cholesterol = Column(Float)
    saturated_fatty_acids = Column(Float)
    trans_fat = Column(Float)
