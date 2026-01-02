"""
Photo and Tag models with relationships.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Table, Column, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


# Many-to-Many association table for photos and tags
photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column(
        "photo_id",
        Integer,
        ForeignKey("photos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Tag(Base):
    """Tag model for categorizing photos."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    photos: Mapped[list["Photo"]] = relationship(
        "Photo", secondary=photo_tags, back_populates="tags", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

    @property
    def photos_count(self) -> int:
        """Get number of photos with this tag."""
        return len(self.photos)


class Photo(Base):
    """Photo model for storing image information."""

    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Cloudinary data
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )

    # Photo info
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="photos", lazy="selectin"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=photo_tags, back_populates="photos", lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="photo", cascade="all, delete-orphan", lazy="selectin"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating", back_populates="photo", cascade="all, delete-orphan", lazy="selectin"
    )
    transformations: Mapped[list["PhotoTransformation"]] = relationship(
        "PhotoTransformation",
        back_populates="original_photo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, user_id={self.user_id})>"

    @property
    def average_rating(self) -> float | None:
        """Calculate average rating for the photo."""
        if not hasattr(self, "ratings") or not self.ratings:
            return None
        return sum(r.score for r in self.ratings) / len(self.ratings)

    @property
    def ratings_count(self) -> int:
        """Get total number of ratings."""
        if not hasattr(self, "ratings"):
            return 0
        return len(self.ratings)


class PhotoTransformation(Base):
    """Model for storing transformed versions of photos."""

    __tablename__ = "photo_transformations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )

    # Transformation data
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    transformation_params: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON string
    qr_code_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Base64 QR code

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    original_photo: Mapped["Photo"] = relationship(
        "Photo", back_populates="transformations"
    )

    def __repr__(self) -> str:
        return f"<PhotoTransformation(id={self.id}, original_photo_id={self.original_photo_id})>"
