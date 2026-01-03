"""
Repository for Photo database operations.
"""

from datetime import datetime
from typing import Literal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.photos.models import Photo, PhotoTransformation, Tag
from src.photos.schemas import PhotoCreate, PhotoUpdate


class TagRepository:
    """Repository for Tag CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Tag | None:
        """Get tag by name.

        **Args:**
        - **name**: String name of the tag.

        **Returns:**
        - **Tag | None**: Tag object if found, else None.
        """
        result = await self.session.execute(
            select(Tag).where(Tag.name == name.lower())
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str) -> Tag:
        """Get existing tag or create new one.

        **Args:**
        - **name**: String name of the tag.

        **Returns:**
        - **Tag**: The existing or newly created Tag object.
        """
        name = name.lower().strip()
        tag = await self.get_by_name(name)

        if tag is None:
            tag = Tag(name=name)
            self.session.add(tag)
            await self.session.commit()
            await self.session.refresh(tag)

        return tag

    async def get_or_create_many(self, names: list[str]) -> list[Tag]:
        """Get or create multiple tags. Limit to 5 tags.

        **Args:**
        - **names**: List of tag names as strings.

        **Returns:**
        - **list[Tag]**: List of Tag objects (maximum 5).
        """
        tags = []
        for name in names[:5]:  # Limit to 5 tags per ТЗ
            if name.strip():
                tag = await self.get_or_create(name)
                tags.append(tag)
        return tags

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Tag]:
        """Get all tags with pagination.

        **Args:**
        - **skip**: Number of records to skip.
        - **limit**: Maximum number of records to return.

        **Returns:**
        - **list[Tag]**: List of all Tag objects within the range.
        """
        result = await self.session.execute(
            select(Tag).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


class PhotoRepository:
    """Repository for Photo CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.tag_repo = TagRepository(session)

    async def get_by_id(self, photo_id: int) -> Photo | None:
        """Get photo by ID with related data.

        **Args:**
        - **photo_id**: Unique identifier of the photo.

        **Returns:**
        - **Photo | None**: Photo object with eager-loaded relationships or None.
        """
        result = await self.session.execute(
            select(Photo)
            .options(
                selectinload(Photo.tags),
                selectinload(Photo.user),
            )
            .where(Photo.id == photo_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Photo]:
        """Get photos by user ID.

        **Args:**
        - **user_id**: ID of the owner.
        - **skip**: Offset for pagination.
        - **limit**: Items per page.

        **Returns:**
        - **list[Photo]**: List of user's Photo objects.
        """
        result = await self.session.execute(
            select(Photo)
            .options(selectinload(Photo.tags))
            .where(Photo.user_id == user_id)
            .order_by(Photo.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Photo]:
        """Get all photos with pagination.

        **Args:**
        - **skip**: Offset for pagination.
        - **limit**: Items per page.

        **Returns:**
        - **list[Photo]**: List of Photo objects.
        """
        result = await self.session.execute(
            select(Photo)
            .options(selectinload(Photo.tags))
            .order_by(Photo.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        """Get total count of photos.

        **Returns:**
        - **int**: Total count.
        """
        result = await self.session.execute(
            select(func.count(Photo.id))
        )
        return result.scalar() or 0

    async def get_user_photos_count(self, user_id: int) -> int:
        """Get count of photos by user.

        **Args:**
        - **user_id**: ID of the user.

        **Returns:**
        - **int**: Count of photos.
        """
        result = await self.session.execute(
            select(func.count(Photo.id)).where(Photo.user_id == user_id)
        )
        return result.scalar() or 0

    async def create(
        self,
        user_id: int,
        url: str,
        cloudinary_public_id: str,
        photo_data: PhotoCreate
    ) -> Photo:
        """Create a new photo.

        **Args:**
        - **user_id**: ID of the creator.
        - **url**: Direct link to the image.
        - **cloudinary_public_id**: ID from Cloudinary storage.
        - **photo_data**: Schema containing description and tags.

        **Returns:**
        - **Photo**: The created Photo object.
        """
        # Get or create tags
        tags = await self.tag_repo.get_or_create_many(photo_data.tags)

        photo = Photo(
            user_id=user_id,
            url=url,
            cloudinary_public_id=cloudinary_public_id,
            description=photo_data.description,
            tags=tags,
        )

        self.session.add(photo)
        await self.session.commit()
        await self.session.refresh(photo)

        return photo

    async def update(self, photo: Photo, photo_data: PhotoUpdate) -> Photo:
        """Update photo description.

        **Args:**
        - **photo**: The existing Photo model instance.
        - **photo_data**: Schema with new description.

        **Returns:**
        - **Photo**: The updated Photo object.
        """
        if photo_data.description is not None:
            photo.description = photo_data.description

        await self.session.commit()
        await self.session.refresh(photo)

        return photo

    async def update_tags(self, photo: Photo, tag_names: list[str]) -> Photo:
        """Update photo tags.

        **Args:**
        - **photo**: The existing Photo model instance.
        - **tag_names**: List of new tag names.

        **Returns:**
        - **Photo**: Photo object with updated tags.
        """
        tags = await self.tag_repo.get_or_create_many(tag_names)
        photo.tags = tags

        await self.session.commit()
        await self.session.refresh(photo)

        return photo

    async def delete(self, photo: Photo) -> bool:
        """Delete a photo.

        **Args:**
        - **photo**: The Photo model instance to delete.

        **Returns:**
        - **bool**: True if successfully deleted.
        """
        await self.session.delete(photo)
        await self.session.commit()
        return True

    async def search_by_description(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> list[Photo]:
        """Search photos by description.

        **Args:**
        - **query**: Search string.
        - **skip/limit**: Pagination parameters.

        **Returns:**
        - **list[Photo]**: List of matching Photo objects.
        """
        result = await self.session.execute(
            select(Photo)
            .options(selectinload(Photo.tags))
            .where(Photo.description.ilike(f"%{query}%"))
            .order_by(Photo.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_tag(
        self, tag_name: str, skip: int = 0, limit: int = 20
    ) -> list[Photo]:
        """Search photos by tag.

        **Args:**
        - **tag_name**: Exact name of the tag (case-insensitive).
        - **skip/limit**: Pagination parameters.

        **Returns:**
        - **list[Photo]**: List of Photo objects containing the tag.
        """
        result = await self.session.execute(
            select(Photo)
            .options(selectinload(Photo.tags))
            .join(Photo.tags)
            .where(Tag.name == tag_name.lower())
            .order_by(Photo.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_advanced(
        self,
        keyword: str | None = None,
        tag: str | None = None,
        user_id: int | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: Literal["created_at", "rating"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Photo], int]:
        """
        Advanced search with multiple filters.
        Returns tuple of (photos, total_count).

        **Args:**
        - **keyword**: Filter by description content.
        - **tag**: Filter by tag name.
        - **user_id**: Filter by creator.
        - **min_rating/max_rating**: Filter by average rating (processed in memory).
        - **date_from/date_to**: Filter by creation timestamp.
        - **sort_by/sort_order**: Define the sorting logic.

        **Returns:**
        - **tuple[list[Photo], int]**: A pair of (list of photos, total items found).
        """
        # Base query with eager loading
        query = (
            select(Photo)
            .options(
                selectinload(Photo.tags),
                selectinload(Photo.user)
            )
        )

        count_query = select(func.count(Photo.id))

        conditions = []

        # Keyword filter (in description)
        if keyword:
            conditions.append(Photo.description.ilike(f"%{keyword}%"))

        # Tag filter
        if tag:
            query = query.join(Photo.tags)
            count_query = count_query.join(Photo.tags)
            conditions.append(Tag.name == tag.lower())

        # User filter
        if user_id:
            conditions.append(Photo.user_id == user_id)

        # Date range filter
        if date_from:
            conditions.append(Photo.created_at >= date_from)
        if date_to:
            conditions.append(Photo.created_at <= date_to)

        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count before pagination
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Sorting
        if sort_by == "created_at":
            order_col = Photo.created_at
        else:
            # For rating sort, we need a subquery (handled in memory)
            order_col = Photo.created_at

        if sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        photos = list(result.scalars().unique().all())

        # Filter by rating in memory if needed (because avg rating is calculated)
        if min_rating is not None or max_rating is not None:
            filtered_photos = []
            for photo in photos:
                avg = photo.average_rating
                if avg is None:
                    avg = 0
                if min_rating is not None and avg < min_rating:
                    continue
                if max_rating is not None and avg > max_rating:
                    continue
                filtered_photos.append(photo)
            photos = filtered_photos
            total = len(photos)

        # Sort by rating in memory if requested
        if sort_by == "rating":
            photos.sort(
                key=lambda p: p.average_rating or 0,
                reverse=(sort_order == "desc")
            )

        return photos, total

    async def search_count(
        self,
        keyword: str | None = None,
        tag: str | None = None,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> int:
        """Get count of photos matching search criteria.

        **Args:**
        - **keyword, tag, user_id, date_from, date_to**: Search filters.

        **Returns:**
        - **int**: Count of matching photos.
        """
        query = select(func.count(Photo.id))

        conditions = []

        if keyword:
            conditions.append(Photo.description.ilike(f"%{keyword}%"))

        if tag:
            query = query.join(Photo.tags)
            conditions.append(Tag.name == tag.lower())

        if user_id:
            conditions.append(Photo.user_id == user_id)

        if date_from:
            conditions.append(Photo.created_at >= date_from)
        if date_to:
            conditions.append(Photo.created_at <= date_to)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalar() or 0


class PhotoTransformationRepository:
    """Repository for PhotoTransformation operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        original_photo_id: int,
        url: str,
        cloudinary_public_id: str,
        transformation_params: str | None = None,
        qr_code_url: str | None = None
    ) -> PhotoTransformation:
        """Create a new photo transformation record.

        **Args:**
        - **original_photo_id**: ID of the source photo.
        - **url**: Link to the transformed image.
        - **cloudinary_public_id**: Cloudinary ID for the new image.
        - **transformation_params**: JSON string with transformation details.
        - **qr_code_url**: Data URI or URL of the generated QR code.

        **Returns:**
        - **PhotoTransformation**: The created transformation record.
        """
        transformation = PhotoTransformation(
            original_photo_id=original_photo_id,
            url=url,
            cloudinary_public_id=cloudinary_public_id,
            transformation_params=transformation_params,
            qr_code_url=qr_code_url,
        )

        self.session.add(transformation)
        await self.session.commit()
        await self.session.refresh(transformation)

        return transformation

    async def get_by_photo(self, photo_id: int) -> list[PhotoTransformation]:
        """Get all transformations for a photo.

        **Args:**
        - **photo_id**: ID of the source photo.

        **Returns:**
        - **list[PhotoTransformation]**: List of transformations, newest first.
        """
        result = await self.session.execute(
            select(PhotoTransformation)
            .where(PhotoTransformation.original_photo_id == photo_id)
            .order_by(PhotoTransformation.created_at.desc())
        )
        return list(result.scalars().all())
