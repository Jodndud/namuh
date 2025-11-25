from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.media_model import Media


class MediaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        mime_type: str,
        owner_id: int,
        s3key_or_url: str,
        seq_no: int = 1,
        media_type: Optional[str] = None,
    ) -> Media:
        media = Media(
            mime_type=mime_type,
            owner_id=owner_id,
            s3key_or_url=s3key_or_url,
            seq_no=seq_no,
            type=media_type,
        )
        self.session.add(media)
        return media

    def find_by_id(self, media_id: int) -> Optional[Media]:
        return self.session.query(Media).filter(Media.id == media_id).first()

    def find_by_owner_id(self, owner_id: int) -> List[Media]:
        return self.session.query(Media).filter(Media.owner_id == owner_id).all()

    def find_by_owner_and_type(self, owner_id: int, media_type: str) -> List[Media]:
        return (
            self.session.query(Media)
            .filter(Media.owner_id == owner_id, Media.type == media_type)
            .order_by(Media.seq_no)
            .all()
        )

    def update(self, media_id: int, **kwargs) -> Optional[Media]:
        media = self.find_by_id(media_id)
        if media:
            for key, value in kwargs.items():
                if hasattr(media, key):
                    setattr(media, key, value)
        return media

    def delete(self, media_id: int) -> bool:
        media = self.find_by_id(media_id)
        if media:
            self.session.delete(media)
            return True
        return False

    def get_max_seq_no(self, owner_id: int, media_type: str) -> Optional[int]:
        result = (
            self.session.query(func.max(Media.seq_no))
            .filter(Media.owner_id == owner_id, Media.type == media_type)
            .scalar()
        )
        return result

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()
