from sqlalchemy import Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Rating(Base):
    """SQLAlchemy model representing a user's rating for a specific photo."""

    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False)

    user: Mapped["User"] = relationship("User", lazy="selectin")
    photo: Mapped["Photo"] = relationship("Photo", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="check_score_range"),
        UniqueConstraint("user_id", "photo_id", name="unique_user_photo_rating"),
    )
