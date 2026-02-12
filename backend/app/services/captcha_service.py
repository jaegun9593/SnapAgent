"""
Self-hosted image CAPTCHA service using Pillow.
In-memory store with TTL expiration, single-use consumption.
"""
import io
import random
import string
import time
import uuid
from base64 import b64encode
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


class CaptchaStore:
    """In-memory CAPTCHA store with 5-minute TTL."""

    TTL_SECONDS = 300  # 5 minutes

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[str, float]] = {}

    def put(self, captcha_id: str, text: str) -> None:
        self._cleanup()
        self._store[captcha_id] = (text.upper(), time.time())

    def pop(self, captcha_id: str) -> Optional[str]:
        """Consume a CAPTCHA (single-use). Returns text or None if expired/missing."""
        self._cleanup()
        entry = self._store.pop(captcha_id, None)
        if entry is None:
            return None
        text, created_at = entry
        if time.time() - created_at > self.TTL_SECONDS:
            return None
        return text

    def _cleanup(self) -> None:
        now = time.time()
        expired = [k for k, (_, t) in self._store.items() if now - t > self.TTL_SECONDS]
        for k in expired:
            del self._store[k]


# Global singleton store
captcha_store = CaptchaStore()

# Characters excluding ambiguous ones (O/0/I/L/1)
CHARS = "".join(
    c for c in string.ascii_uppercase + string.digits if c not in "OIL01"
)


class CaptchaService:
    """Generate image CAPTCHAs using Pillow."""

    WIDTH = 200
    HEIGHT = 70
    LENGTH = 6

    def generate(self) -> Tuple[str, str]:
        """
        Generate a CAPTCHA image.

        Returns:
            (captcha_id, image_base64_data_uri)
        """
        text = "".join(random.choices(CHARS, k=self.LENGTH))
        captcha_id = str(uuid.uuid4())

        image = self._render(text)

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64 = b64encode(buf.getvalue()).decode()
        data_uri = f"data:image/png;base64,{b64}"

        captcha_store.put(captcha_id, text)
        return captcha_id, data_uri

    @staticmethod
    def verify(captcha_id: str, captcha_text: str) -> bool:
        """Verify a CAPTCHA answer (case-insensitive, single-use)."""
        expected = captcha_store.pop(captcha_id)
        if expected is None:
            return False
        return expected == captcha_text.upper()

    def _render(self, text: str) -> Image.Image:
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Try to use a built-in font with reasonable size
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Draw each character with random color and slight position offset
        x_start = 15
        for i, ch in enumerate(text):
            color = (
                random.randint(0, 150),
                random.randint(0, 150),
                random.randint(0, 150),
            )
            y_offset = random.randint(-5, 10)
            draw.text((x_start + i * 28, 12 + y_offset), ch, fill=color, font=font)

        # Noise lines
        for _ in range(random.randint(5, 8)):
            x1, y1 = random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT)
            x2, y2 = random.randint(0, self.WIDTH), random.randint(0, self.HEIGHT)
            color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200),
            )
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

        # Noise dots
        for _ in range(random.randint(100, 200)):
            x, y = random.randint(0, self.WIDTH - 1), random.randint(0, self.HEIGHT - 1)
            color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200),
            )
            draw.point((x, y), fill=color)

        return img
