from sqlalchemy import Column, Integer, String

from .settings import Base


class Trigger(Base):

    __tablename__ = "trigger"

    id = Column(Integer, primary_key=True)
    trigger = Column(String)
    alias = Column(String)
    response = Column(String)
    title = Column(String)
    description = Column(String)
    right_small_image_url = Column(String)
    big_image_url = Column(String)


class Currency(Base):

    __tablename__ = "currency"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    bonus = Column(String)
    money = Column(String)


class Shop(Base):

    __tablename__ = "shop"

    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    memo = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)

