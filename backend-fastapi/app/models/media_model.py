from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()

KST = timezone(timedelta(hours=9))


def get_kst_now():
    return datetime.now(KST)


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mime_type = Column(String(30), nullable=False)
    owner_id = Column(Integer, nullable=False)
    s3key_or_url = Column(String(255), nullable=False)
    seq_no = Column(Integer, nullable=True)
    type = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_kst_now, nullable=False)
    updated_at = Column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False,
    )
