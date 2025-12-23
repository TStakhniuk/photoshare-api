from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Photo(Base):
    """
    SQLAlchemy model representing a photo.
    """

    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="photo", cascade="all, delete-orphan"
    )
