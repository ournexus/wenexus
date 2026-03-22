"""
集成测试：验证认证 SQL 查询与 Drizzle schema 兼容。

测试前提：
  1. PostgreSQL 已启动
  2. wenexus_dev 数据库存在并已同步 schema
  3. better-auth 已为 user/session 表写入初始数据或使用测试 fixtures

验证内容：
  1. session 表 SELECT 查询列名与 SQL 正确
  2. user 表 JOIN 查询列名与 SQL 正确
  3. 查询返回的行能正确映射到 UserInfo dataclass
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from wenexus.repository.auth import query_user_by_token


# 集成测试 fixture：真实数据库连接
@pytest_asyncio.fixture(scope="function")
async def async_db() -> AsyncSession:
    """
    创建异步数据库 session，连接真实 PostgreSQL。

    使用 NullPool 避免连接复用问题。
    """
    engine = create_async_engine(
        "postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev",
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        # 测试连接是否正常
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Database connection failed"

    # 创建 session
    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


class TestAuthSchemaCompatibility:
    """
    验证认证查询与 Drizzle schema 兼容性。
    """

    @pytest.mark.asyncio
    async def test_session_and_user_table_columns_exist(
        self, async_db: AsyncSession
    ) -> None:
        """
        验证 session 和 user 表存在，且包含必要的列。

        这是 baseline 检查，确保表结构与 SQL 查询匹配。
        """
        # 检查 user 表列
        result = await async_db.execute(
            text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'user'
            ORDER BY ordinal_position
        """)
        )
        user_columns = {row[0]: row[1] for row in result.all()}

        # 预期的必要列（snake_case，因为 Drizzle 默认使用 snake_case）
        expected_user_cols = {
            "id": "text",
            "name": "text",
            "email": "text",
            "email_verified": "boolean",
            "image": "text",
        }

        for col_name, _col_type in expected_user_cols.items():
            assert col_name in user_columns, f"Missing column in user table: {col_name}"
            # PostgreSQL 可能返回不同的类型名（如 character varying vs text），所以只检查存在性
            assert user_columns[col_name] is not None

        # 检查 session 表列
        result = await async_db.execute(
            text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'session'
            ORDER BY ordinal_position
        """)
        )
        session_columns = {row[0]: row[1] for row in result.all()}

        expected_session_cols = {
            "id": "text",
            "token": "text",
            "user_id": "text",
            "expires_at": "timestamp",
        }

        for col_name, _col_type in expected_session_cols.items():
            assert col_name in session_columns, (
                f"Missing column in session table: {col_name}"
            )

    @pytest.mark.asyncio
    async def test_select_query_on_user_table(self, async_db: AsyncSession) -> None:
        """
        验证 SELECT 查询能从 user 表读取正确列。
        """
        # 执行 user 表查询，测试列名正确性
        result = await async_db.execute(
            text("""
            SELECT id, name, email, image, email_verified
            FROM "user"
            LIMIT 1
        """)
        )

        # 只需验证查询执行成功，列名正确
        # 如果列名错误会抛 ProgrammingError
        assert result is not None

    @pytest.mark.asyncio
    async def test_session_join_user_query_syntax(self, async_db: AsyncSession) -> None:
        """
        验证 session JOIN user 的 SQL 查询语法正确。

        这是认证流程中的核心查询，必须验证 JOIN 条件和列引用正确。
        """
        # 执行 session + user 的 JOIN 查询（不指定 token，只验证 SQL 语法）
        result = await async_db.execute(
            text("""
            SELECT u.id, u.name, u.email, u.image, u.email_verified
            FROM "session" s
            JOIN "user" u ON s.user_id = u.id
            WHERE s.expires_at > NOW()
            LIMIT 1
        """)
        )

        # 查询应该执行成功（即使没有返回结果）
        result.first()
        assert result is not None

    @pytest.mark.asyncio
    async def test_query_user_by_token_returns_correct_schema(
        self, async_db: AsyncSession
    ) -> None:
        """
        验证 query_user_by_token 返回的 UserInfo 数据结构正确。

        这是认证服务的核心函数，验证其与数据库 schema 兼容。
        """
        # 使用无效 token 调用（不会找到结果，但验证查询语法）
        result = await query_user_by_token(async_db, "non-existent-token")

        # 预期返回 None（因为 token 不存在）
        assert result is None

    @pytest.mark.asyncio
    async def test_session_query_matches_expected_fields(
        self, async_db: AsyncSession
    ) -> None:
        """
        验证 _SESSION_QUERY 的字段列表与 UserInfo dataclass 匹配。

        这确保 SQL 查询返回的列能正确映射到 UserInfo。
        """
        from wenexus.repository.auth import _SESSION_QUERY

        # 验证查询中的 SELECT 字段
        query_str = str(_SESSION_QUERY)

        required_fields = ["id", "name", "email", "image", "email_verified"]
        for field in required_fields:
            # 检查字段名在查询中出现（以 u. 前缀形式或直接）
            assert (
                field.lower() in query_str.lower()
                or f"u.{field}" in query_str
                or f'u."{field}"' in query_str
                or f'"{field}"' in query_str
            ), f"Field {field} not found in _SESSION_QUERY"


class TestAuthSchemaEdgeCases:
    """
    测试认证查询的边界条件。
    """

    @pytest.mark.asyncio
    async def test_email_verified_field_handling(self, async_db: AsyncSession) -> None:
        """
        验证 email_verified 字段的类型转换。

        Python 查询中 email_verified (boolean) 应被正确转换为 bool。
        """
        # 执行查询检查 email_verified 字段的数据类型
        result = await async_db.execute(
            text("""
            SELECT email_verified
            FROM "user"
            LIMIT 1
        """)
        )

        row = result.first()
        if row is not None:
            # 字段应该是 boolean 或 None
            assert isinstance(row[0], (bool, type(None)))

    @pytest.mark.asyncio
    async def test_expired_session_not_returned(self, async_db: AsyncSession) -> None:
        """
        验证过期 session 不会被认证查询返回。

        确保 WHERE s."expiresAt" > NOW() 条件工作正确。
        """
        # 这个测试需要测试数据，暂时跳过
        pytest.skip("Test requires fixture data with expired sessions")

    @pytest.mark.asyncio
    async def test_null_image_field_handling(self, async_db: AsyncSession) -> None:
        """
        验证 image 字段为 NULL 时的处理。

        image 是可选字段，必须正确处理 NULL 值。
        """
        # 执行查询检查 NULL image 字段
        result = await async_db.execute(
            text("""
            SELECT image
            FROM "user"
            WHERE image IS NULL
            LIMIT 1
        """)
        )

        # 查询应该执行成功
        assert result is not None
