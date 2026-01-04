import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from fastapi import UploadFile

from src.services.cloudinary import CloudinaryService


@pytest.mark.asyncio
async def test_upload_image(monkeypatch):
    """Test upload_image method returns correct dict."""

    async def fake_read():
        return b"fake image bytes"

    file = UploadFile(filename="test.jpg", file=BytesIO(b""))
    file.read = fake_read

    def fake_upload(contents, folder, resource_type, allowed_formats):
        return {"secure_url": "http://cloudinary.com/fake.jpg", "public_id": "fake_id"}

    monkeypatch.setattr("cloudinary.uploader.upload", fake_upload)

    result = await CloudinaryService.upload_image(file)
    assert result["url"] == "http://cloudinary.com/fake.jpg"
    assert result["public_id"] == "fake_id"


def test_delete_image(monkeypatch):
    """Test delete_image returns True if successful."""

    monkeypatch.setattr("cloudinary.uploader.destroy", lambda public_id: {"result": "ok"})
    assert CloudinaryService.delete_image("fake_id") is True

    monkeypatch.setattr("cloudinary.uploader.destroy", lambda public_id: {"result": "not found"})
    assert CloudinaryService.delete_image("fake_id") is False


def test_transform_image(monkeypatch):
    """Test transform_image returns correct URL."""

    mock_build_url = MagicMock(return_value="http://cloudinary.com/transformed.jpg")
    monkeypatch.setattr("cloudinary.CloudinaryImage", lambda public_id: MagicMock(build_url=mock_build_url))

    url = CloudinaryService.transform_image("fake_id", transformation={"crop": "fill"})
    assert url == "http://cloudinary.com/transformed.jpg"
    mock_build_url.assert_called_once()


@pytest.mark.parametrize("method_name,args", [
    ("get_circle_crop_url", (200,)),
    ("get_rounded_corners_url", (15,)),
    ("get_grayscale_url", ()),
    ("get_sepia_url", ()),
    ("get_blur_url", (300,)),
])
def test_specific_transformations(monkeypatch, method_name, args):
    """Test specific transformation methods return URL."""

    mock_build_url = MagicMock(return_value="http://cloudinary.com/transformed_specific.jpg")
    monkeypatch.setattr("cloudinary.CloudinaryImage", lambda public_id: MagicMock(build_url=mock_build_url))

    method = getattr(CloudinaryService, method_name)
    url = method("fake_id", *args) if args else method("fake_id")
    assert url == "http://cloudinary.com/transformed_specific.jpg"
    mock_build_url.assert_called_once()


def test_add_text_overlay(monkeypatch):
    """Test add_text_overlay returns URL."""

    mock_build_url = MagicMock(return_value="http://cloudinary.com/text_overlay.jpg")
    monkeypatch.setattr("cloudinary.CloudinaryImage", lambda public_id: MagicMock(build_url=mock_build_url))

    url = CloudinaryService.add_text_overlay("fake_id", text="Hello", font_size=30)
    assert url == "http://cloudinary.com/text_overlay.jpg"
    mock_build_url.assert_called_once()


def test_resize_image(monkeypatch):
    """Test resize_image returns URL."""

    mock_build_url = MagicMock(return_value="http://cloudinary.com/resized.jpg")
    monkeypatch.setattr("cloudinary.CloudinaryImage", lambda public_id: MagicMock(build_url=mock_build_url))

    url = CloudinaryService.resize_image("fake_id", width=100, height=100)
    assert url == "http://cloudinary.com/resized.jpg"
    mock_build_url.assert_called_once()


def test_transform_image_default(monkeypatch):
    """Test transform_image handles None transformation (default value)."""

    mock_build_url = MagicMock(return_value="http://cloudinary.com/default.jpg")
    monkeypatch.setattr("cloudinary.CloudinaryImage", lambda public_id: MagicMock(build_url=mock_build_url))

    url = CloudinaryService.transform_image("fake_id")

    assert url == "http://cloudinary.com/default.jpg"

    mock_build_url.assert_called_once_with(transformation={}, secure=True)
