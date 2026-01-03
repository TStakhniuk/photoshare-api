"""
Photos module for PhotoShare API.
Implements CRUD operations for photos, tags, and transformations.
"""

from src.photos.models import Photo, Tag, PhotoTransformation, photo_tags
from src.photos.schemas import (
    PhotoCreate,
    PhotoUpdate,
    PhotoResponse,
    PhotoListResponse,
    PhotoTransformRequest,
    PhotoTransformResponse,
    TagBase,
    TagCreate,
    TagResponse,
    PhotoSearchParams,
)
from src.photos.repository import (
    PhotoRepository,
    TagRepository,
    PhotoTransformationRepository,
)
from src.photos.routes import router

__all__ = [
    "Photo",
    "Tag",
    "PhotoTransformation",
    "photo_tags",
    "PhotoCreate",
    "PhotoUpdate",
    "PhotoResponse",
    "PhotoListResponse",
    "PhotoTransformRequest",
    "PhotoTransformResponse",
    "TagBase",
    "TagCreate",
    "TagResponse",
    "PhotoSearchParams",
    "PhotoRepository",
    "TagRepository",
    "PhotoTransformationRepository",
    "router",
]
