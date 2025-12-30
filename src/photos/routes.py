"""
Photo routes for CRUD operations and transformations.
"""

import json
import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.db import get_db
from src.auth.dependencies import get_current_user, RoleChecker
from src.users.models import User
from src.users.enums import RoleEnum

from src.photos.schemas import (
    PhotoCreate,
    PhotoUpdate,
    PhotoResponse,
    PhotoListResponse,
    PhotoTransformRequest,
    PhotoTransformResponse,
)
from src.photos.repository import PhotoRepository, PhotoTransformationRepository
from src.services.cloudinary import CloudinaryService, AVAILABLE_TRANSFORMATIONS
from src.services.qrcode import QRCodeService


router = APIRouter()


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    tags: str | None = Form(None, description="Comma-separated tags (max 5)"),
):
    """
    Upload a new photo.

    - Supports JPG, JPEG, PNG, GIF, WEBP formats
    - Maximum 5 tags allowed

    **Args:**
    - **file**: The image file to upload (JPG, PNG, etc.).
    - **description**: Optional text description of the photo.
    - **tags**: Optional comma-separated list of tags (e.g., "nature,vacation"). Max 5 tags.

    **Returns:**
    - **PhotoResponse**: The created photo object including URL and metadata.
    """

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()][:5]

    # Upload to Cloudinary
    try:
        upload_result = await CloudinaryService.upload_image(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

    # Create photo record
    photo_repo = PhotoRepository(db)
    photo_data = PhotoCreate(description=description, tags=tag_list)

    photo = await photo_repo.create(
        user_id=current_user.id,
        url=upload_result["url"],
        cloudinary_public_id=upload_result["public_id"],
        photo_data=photo_data,
    )

    return photo


@router.get("/", response_model=PhotoListResponse)
async def get_photos(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """Get all photos with pagination.

    **Args:**
    - **page**: Page number (starts from 1).
    - **size**: Number of items per page (max 100).

    **Returns:**
    - **PhotoListResponse**: A paginated list of photos with total count information.
    """

    photo_repo = PhotoRepository(db)

    skip = (page - 1) * size
    photos = await photo_repo.get_all(skip=skip, limit=size)
    total = await photo_repo.get_total_count()
    pages = (total + size - 1) // size

    return PhotoListResponse(
        items=photos,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/search", response_model=PhotoListResponse)
async def search_photos(
    db: AsyncSession = Depends(get_db),
    keyword: str | None = Query(None, description="Search in description"),
    tag: str | None = Query(None, description="Filter by tag name"),
    user_id: int | None = Query(None, description="Filter by user ID"),
    min_rating: float | None = Query(None, ge=1, le=5, description="Minimum average rating"),
    max_rating: float | None = Query(None, ge=1, le=5, description="Maximum average rating"),
    date_from: datetime | None = Query(None, description="Photos created after this date"),
    date_to: datetime | None = Query(None, description="Photos created before this date"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating)$", description="Sort by field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    Search and filter photos.

    Supports:
    - Keyword search in description
    - Filter by tag
    - Filter by user
    - Filter by rating range
    - Filter by date range
    - Sort by date or rating

    **Args:**
    - **keyword**: Search in description.
    - **tag**: Filter by specific tag.
    - **user_id**: Filter by owner's ID.
    - **min_rating / max_rating**: Filter by average rating range (1-5).
    - **date_from / date_to**: Range for creation date.
    - **sort_by**: Field to sort by ('created_at' or 'rating').

    **Returns:**
    - **PhotoListResponse**: Filtered and paginated list of photos.
    """
    photo_repo = PhotoRepository(db)

    skip = (page - 1) * size
    photos, total = await photo_repo.search_advanced(
        keyword=keyword,
        tag=tag,
        user_id=user_id,
        min_rating=min_rating,
        max_rating=max_rating,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,  # type: ignore
        sort_order=sort_order,  # type: ignore
        skip=skip,
        limit=size,
    )

    pages = (total + size - 1) // size if total > 0 else 0

    return PhotoListResponse(
        items=photos,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a photo by ID.

    **Args:**
    - **photo_id**: Unique identifier of the photo.

    **Returns:**
    - **PhotoResponse**: Full details of the photo.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    return photo


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    photo_data: PhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update photo description.

    - Users can update their own photos
    - Admins can update any photo

    **Args:**
    - **photo_id**: ID of the photo to update.
    - **photo_data**: New data for the photo.

    **Returns:**
    - **PhotoResponse**: The updated photo object.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Check permissions
    if photo.user_id != current_user.id and current_user.role.name != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    photo = await photo_repo.update(photo, photo_data)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a photo.

    - Users can delete their own photos
    - Admins can delete any photo

    **Args:**
    - **photo_id**: ID of the photo to delete.

    **Returns:**
    - **204 No Content** on success.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Check permissions
    if photo.user_id != current_user.id and current_user.role.name != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Delete from Cloudinary
    try:
        CloudinaryService.delete_image(photo.cloudinary_public_id)
    except Exception:
        pass  # Continue even if Cloudinary deletion fails

    # Delete from database
    await photo_repo.delete(photo)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{photo_id}/transform", response_model=PhotoTransformResponse)
async def transform_photo(
    photo_id: int,
    transform_data: PhotoTransformRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Apply transformation to a photo.

    Available transformations:
    - circle: Circular crop
    - rounded: Rounded corners
    - grayscale: Black and white
    - sepia: Sepia tone
    - blur: Blur effect

    **Args:**
    - **photo_id**: ID of the source photo.
    - **transform_data**: Specification of the transformation (circle, blur, etc.).

    **Returns:**
    - **PhotoTransformResponse**: URL of the transformed image and a QR code link.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Validate transformation type
    if transform_data.transformation not in AVAILABLE_TRANSFORMATIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transformation. Available: {list(AVAILABLE_TRANSFORMATIONS.keys())}"
        )

    # Apply transformation
    public_id = photo.cloudinary_public_id

    if transform_data.transformation == "circle":
        size = transform_data.size or 200
        transformed_url = CloudinaryService.get_circle_crop_url(public_id, size)
        params = {"type": "circle", "size": size}
    elif transform_data.transformation == "rounded":
        radius = transform_data.radius or 20
        transformed_url = CloudinaryService.get_rounded_corners_url(public_id, radius)
        params = {"type": "rounded", "radius": radius}
    elif transform_data.transformation == "grayscale":
        transformed_url = CloudinaryService.get_grayscale_url(public_id)
        params = {"type": "grayscale"}
    elif transform_data.transformation == "sepia":
        transformed_url = CloudinaryService.get_sepia_url(public_id)
        params = {"type": "sepia"}
    elif transform_data.transformation == "blur":
        strength = transform_data.blur_strength or 500
        transformed_url = CloudinaryService.get_blur_url(public_id, strength)
        params = {"type": "blur", "strength": strength}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown transformation"
        )

    # Generate QR code for the transformed image
    qr_code_data_uri = QRCodeService.generate_qr_code_data_uri(transformed_url)

    # Save transformation record
    transform_repo = PhotoTransformationRepository(db)
    unique_suffix = int(time.time() * 1000)
    transformation = await transform_repo.create(
        original_photo_id=photo.id,
        url=transformed_url,
        cloudinary_public_id=f"{public_id}_{transform_data.transformation}_{unique_suffix}",
        transformation_params=json.dumps(params),
        qr_code_url=qr_code_data_uri,
    )

    return transformation


@router.get("/{photo_id}/transformations", response_model=list[PhotoTransformResponse])
async def get_photo_transformations(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all transformations for a photo.

    **Args:**
    - **photo_id**: ID of the source photo.

    **Returns:**
    - **List[PhotoTransformResponse]**: Array of transformation records.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    transform_repo = PhotoTransformationRepository(db)
    transformations = await transform_repo.get_by_photo(photo_id)

    return transformations


@router.get("/{photo_id}/qr")
async def get_photo_qr_code(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get QR code for photo URL.

    **Args:**
    - **photo_id**: ID of the photo.

    **Returns:**
    - **PNG image**: Direct byte stream of the QR code.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Generate QR code for the photo URL
    qr_bytes = QRCodeService.generate_qr_code(photo.url)

    return Response(
        content=qr_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=qr_photo_{photo_id}.png"}
    )


@router.get("/user/{user_id}", response_model=list[PhotoResponse])
async def get_user_photos(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get all photos by a specific user.

    **Args:**
    - **user_id**: ID of the user.
    - **skip**: Number of records to skip.
    - **limit**: Maximum records to return.

    **Returns:**
    - **List[PhotoResponse]**: List of user's photos.
    """
    photo_repo = PhotoRepository(db)
    photos = await photo_repo.get_by_user(user_id, skip=skip, limit=limit)

    return photos
