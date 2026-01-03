"""
Cloudinary service for image upload and transformations.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile

from src.conf.settings import settings


# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


class CloudinaryService:
    """Service for Cloudinary operations."""

    @staticmethod
    async def upload_image(file: UploadFile, folder: str = "photoshare") -> dict:
        """
        Upload an image to Cloudinary.

        Args:
            file: File to upload
            folder: Cloudinary folder name

        Returns:
            Dict with url and public_id
        """
        contents = await file.read()

        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "gif", "webp"],
        )

        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
        }

    @staticmethod
    def delete_image(public_id: str) -> bool:
        """
        Delete an image from Cloudinary.

        Args:
            public_id: Cloudinary public ID

        Returns:
            True if deleted successfully
        """
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"

    @staticmethod
    def transform_image(
        public_id: str,
        transformation: dict | None = None
    ) -> str:
        """
        Get transformed image URL.

        Args:
            public_id: Cloudinary public ID
            transformation: Transformation parameters

        Returns:
            Transformed image URL
        """
        if transformation is None:
            transformation = {}

        url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation,
            secure=True
        )

        return url

    @staticmethod
    def get_circle_crop_url(public_id: str, size: int = 200) -> str:
        """Get image with circular crop."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"width": size, "height": size, "crop": "fill", "gravity": "face"},
                {"radius": "max"},
            ],
            secure=True
        )

    @staticmethod
    def get_rounded_corners_url(public_id: str, radius: int = 20) -> str:
        """Get image with rounded corners."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"radius": radius},
            ],
            secure=True
        )

    @staticmethod
    def get_grayscale_url(public_id: str) -> str:
        """Get grayscale image."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"effect": "grayscale"},
            ],
            secure=True
        )

    @staticmethod
    def get_sepia_url(public_id: str) -> str:
        """Get sepia-toned image."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"effect": "sepia"},
            ],
            secure=True
        )

    @staticmethod
    def get_blur_url(public_id: str, strength: int = 500) -> str:
        """Get blurred image."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"effect": f"blur:{strength}"},
            ],
            secure=True
        )

    @staticmethod
    def add_text_overlay(
        public_id: str,
        text: str,
        font_size: int = 40,
        color: str = "white",
        gravity: str = "south"
    ) -> str:
        """Add text overlay to image."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {
                    "overlay": {
                        "font_family": "Arial",
                        "font_size": font_size,
                        "text": text,
                    },
                    "color": color,
                    "gravity": gravity,
                },
            ],
            secure=True
        )

    @staticmethod
    def resize_image(public_id: str, width: int, height: int, crop: str = "fill") -> str:
        """Resize image to specific dimensions."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {"width": width, "height": height, "crop": crop},
            ],
            secure=True
        )


# Available transformations for API
AVAILABLE_TRANSFORMATIONS = {
    "circle": "Circular crop",
    "rounded": "Rounded corners",
    "grayscale": "Black and white",
    "sepia": "Sepia tone",
    "blur": "Blur effect",
}
