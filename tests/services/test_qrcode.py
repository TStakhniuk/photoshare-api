import pytest
import base64
from io import BytesIO
from PIL import Image
from src.services.qrcode import QRCodeService


def test_generate_qr_code_bytes():
    """Test QR code generation returns bytes."""
    data = "https://example.com"
    qr_bytes = QRCodeService.generate_qr_code(data)
    
    assert isinstance(qr_bytes, bytes)
    assert len(qr_bytes) > 0

    # Check if bytes represent a valid PNG
    img = Image.open(BytesIO(qr_bytes))
    assert img.format == "PNG"


def test_generate_qr_code_base64():
    """Test QR code generation as base64 string."""
    data = "Hello World"
    qr_base64 = QRCodeService.generate_qr_code_base64(data)
    
    assert isinstance(qr_base64, str)
    decoded_bytes = base64.b64decode(qr_base64)
    
    # Check if decoded bytes are valid PNG
    img = Image.open(BytesIO(decoded_bytes))
    assert img.format == "PNG"


def test_generate_qr_code_data_uri():
    """Test QR code generation as data URI."""
    data = "Test Data"
    data_uri = QRCodeService.generate_qr_code_data_uri(data)
    
    assert isinstance(data_uri, str)
    assert data_uri.startswith("data:image/png;base64,")

    base64_part = data_uri.split(",", 1)[1]
    decoded_bytes = base64.b64decode(base64_part)
    
    img = Image.open(BytesIO(decoded_bytes))
    assert img.format == "PNG"
