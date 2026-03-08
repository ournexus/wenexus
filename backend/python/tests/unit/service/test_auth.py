"""Tests for service.auth and util.schema: UserInfo DTO and authenticate logic."""

from unittest.mock import AsyncMock, patch

import pytest

from wenexus.util.schema import UserInfo


class TestUserInfo:
    """测试 UserInfo dataclass 结构。"""

    def test_create_user_info(self) -> None:
        """能正常创建 UserInfo 实例，字段正确。"""
        user = UserInfo(
            id="user-1",
            name="Test User",
            email="test@example.com",
            image=None,
            email_verified=True,
        )
        assert user.id == "user-1"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.image is None
        assert user.email_verified is True

    def test_user_info_with_image(self) -> None:
        """image 字段可选，可以是字符串。"""
        user = UserInfo(
            id="user-2",
            name="Another User",
            email="other@example.com",
            image="https://example.com/avatar.jpg",
            email_verified=False,
        )
        assert user.image == "https://example.com/avatar.jpg"
        assert user.email_verified is False


class TestAuthenticate:
    """测试 service.auth.authenticate 业务逻辑。"""

    @pytest.mark.asyncio
    async def test_returns_user_when_token_valid(self) -> None:
        """有效 token 应返回 UserInfo。"""
        expected = UserInfo(
            id="u1", name="A", email="a@b.com", image=None, email_verified=True
        )
        mock_db = AsyncMock()
        with patch("wenexus.service.auth.query_user_by_token", return_value=expected):
            from wenexus.service.auth import authenticate

            result = await authenticate(mock_db, "valid-token")
        assert result == expected

    @pytest.mark.asyncio
    async def test_returns_none_when_token_invalid(self) -> None:
        """无效 token 应返回 None。"""
        mock_db = AsyncMock()
        with patch("wenexus.service.auth.query_user_by_token", return_value=None):
            from wenexus.service.auth import authenticate

            result = await authenticate(mock_db, "bad-token")
        assert result is None
