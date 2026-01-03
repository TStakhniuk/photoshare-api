"""
QR code generation service.
"""

import io
import base64
import qrcode
from qrcode.image.pil import PilImage


class QRCodeService:
    """Service for QR code generation."""

    @staticmethod
    def generate_qr_code(data: str, box_size: int = 10, border: int = 4) -> bytes:
        """
        Generate QR code image as bytes.

        Args:
            data: Data to encode in QR code
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            QR code image as bytes (PNG format)
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img: PilImage = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.getvalue()

    @staticmethod
    def generate_qr_code_base64(data: str, box_size: int = 10, border: int = 4) -> str:
        """
        Generate QR code as base64 encoded string.

        Args:
            data: Data to encode in QR code
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            Base64 encoded QR code image
        """
        qr_bytes = QRCodeService.generate_qr_code(data, box_size, border)
        return base64.b64encode(qr_bytes).decode("utf-8")

    @staticmethod
    def generate_qr_code_data_uri(data: str, box_size: int = 10, border: int = 4) -> str:
        """
        Generate QR code as data URI for embedding in HTML.

        Args:
            data: Data to encode in QR code
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            Data URI string for QR code image
        """
        base64_str = QRCodeService.generate_qr_code_base64(data, box_size, border)
        return f"data:image/png;base64,{base64_str}"
