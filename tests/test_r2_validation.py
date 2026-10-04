import unittest

from fastapi import HTTPException

from src.features.r2.validation import validate_image


class R2ValidationTests(unittest.TestCase):
    def test_rejects_heic_magic_bytes(self):
        heic_header = b"\x00\x00\x00\x18ftypheic" + b"\x00" * 8

        with self.assertRaises(HTTPException) as ctx:
            validate_image("image/jpeg", heic_header, "photo.jpg")

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("HEIC", ctx.exception.detail)

    def test_accepts_jpeg_when_content_matches(self):
        jpeg = b"\xff\xd8\xff" + b"\x00" * 13

        mime = validate_image("image/jpeg", jpeg)

        self.assertEqual(mime, "image/jpeg")


if __name__ == "__main__":
    unittest.main()
