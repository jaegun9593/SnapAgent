"""
Pydantic schemas for authentication endpoints.
"""
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Request schema for user registration.

    KISA 개인정보보호 가이드라인 비밀번호 정책:
    - 3종 이상 조합(대문자/소문자/숫자/특수문자): 최소 8자
    - 2종 조합: 최소 10자
    - 연속 동일문자 3회 이상 금지 (aaa, 111)
    - 연속 순차문자 3회 이상 금지 (abc, 123, cba, 321)
    - 이메일(아이디) 포함 금지
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (KISA compliant)")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    captcha_id: str = Field(..., description="CAPTCHA identifier")
    captcha_text: str = Field(..., description="User-entered CAPTCHA text")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str, info) -> str:  # noqa: N805
        # 문자 종류 판별
        has_upper = bool(re.search(r"[A-Z]", v))
        has_lower = bool(re.search(r"[a-z]", v))
        has_digit = bool(re.search(r"[0-9]", v))
        has_special = bool(re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:'\",.<>?/`~\\]", v))
        type_count = sum([has_upper, has_lower, has_digit, has_special])

        # 3종 이상 조합 → 8자, 2종 조합 → 10자
        if type_count >= 3 and len(v) < 8:
            raise ValueError("3종 이상 조합 시 최소 8자 이상이어야 합니다")
        if type_count == 2 and len(v) < 10:
            raise ValueError("2종 조합 시 최소 10자 이상이어야 합니다")
        if type_count < 2:
            raise ValueError("영문 대문자, 소문자, 숫자, 특수문자 중 최소 2종 이상을 포함해야 합니다")

        # 연속 동일문자 3회 금지
        for i in range(len(v) - 2):
            if v[i] == v[i + 1] == v[i + 2]:
                raise ValueError("동일 문자를 3회 이상 연속 사용할 수 없습니다")

        # 연속 순차문자 3회 금지 (abc, 123, cba, 321)
        for i in range(len(v) - 2):
            c0, c1, c2 = ord(v[i]), ord(v[i + 1]), ord(v[i + 2])
            if c1 - c0 == 1 and c2 - c1 == 1:
                raise ValueError("연속된 순차 문자를 3자 이상 사용할 수 없습니다")
            if c0 - c1 == 1 and c1 - c2 == 1:
                raise ValueError("연속된 순차 문자를 3자 이상 사용할 수 없습니다")

        # 이메일 포함 금지
        email = info.data.get("email", "")
        if email:
            local_part = email.split("@")[0].lower()
            if len(local_part) >= 4 and local_part in v.lower():
                raise ValueError("비밀번호에 이메일 아이디를 포함할 수 없습니다")

        return v


class CaptchaResponse(BaseModel):
    """Response schema for CAPTCHA generation."""

    captcha_id: str = Field(..., description="CAPTCHA identifier for verification")
    image_base64: str = Field(..., description="Base64-encoded PNG image data URI")


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response schema for token endpoints."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class LogoutResponse(BaseModel):
    """Response schema for logout."""

    message: str = Field(default="Logged out successfully")
