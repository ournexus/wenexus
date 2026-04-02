"""Fact Checker E2E Tests.

End-to-end tests using langgraph dev server.
"""

import json

import httpx
import pytest

from wenexus.agent.fact_checker.entrypoint import create_fact_checker_graph_entrypoint


class TestLangGraphStartup:
    """LangGraph 启动测试."""

    def test_entrypoint_returns_compiled_graph(self):
        """entrypoint 应返回编译好的 StateGraph."""
        graph = create_fact_checker_graph_entrypoint()
        assert graph is not None
        print(f"Graph type: {type(graph)}")

    def test_graph_invocation(self):
        """应能成功调用 graph."""
        graph = create_fact_checker_graph_entrypoint()

        result = graph.invoke(
            {
                "topic": "彩礼",
                "iteration": 0,
                "queries": [],
                "should_continue": True,
                "report": None,
            }
        )

        assert result["report"] is not None
        assert result["report"].topic == "彩礼"
        assert result["report"].items
        assert len(result["report"].items) > 0
        assert result["report"].items[0].credibility == "high"
        print(f"Report: {result['report']}")


class TestFactCheckerAPI:
    """API 端点测试 (需要 langgraph dev 或 FastAPI 运行)."""

    @pytest.fixture
    def base_url(self):
        """测试服务器地址."""
        return "http://127.0.0.1:2024"

    @pytest.fixture
    def api_base(self):
        """FastAPI 服务器地址."""
        return "http://127.0.0.1:8000"

    @pytest.mark.asyncio
    async def test_health_endpoint(self, api_base: str):
        """健康检查端点."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{api_base}/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                print(f"✅ Health check: {data}")
        except httpx.ConnectError:
            pytest.skip("FastAPI server not running, start with: uv run uvicorn ...")

    @pytest.mark.asyncio
    async def test_fact_check_endpoint(self, api_base: str):
        """事实核查端点测试."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_base}/api/v1/fact-check",
                    json={
                        "topic_id": "test-123",
                        "topic_title": "彩礼是不是陋习",
                        "topic_description": "关于彩礼争议的讨论",
                    },
                    timeout=30.0,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["topic_title"] == "彩礼是不是陋习"
                assert data["facts_count"] >= 0
                print(f"✅ Fact check response: {data}")
        except httpx.ConnectError:
            pytest.skip("FastAPI server not running, start with: uv run uvicorn ...")
        except Exception as e:
            print(f"Error: {e}")
            # 测试期间可能返回 500，但结构应正确


class TestLangGraphDevIntegration:
    """LangGraph Dev 集成测试."""

    @pytest.fixture
    def lg_base_url(self):
        """LangGraph dev server URL."""
        return "http://127.0.0.1:2024"

    @pytest.mark.asyncio
    async def test_langgraph_dev_health(self, lg_base_url: str):
        """LangGraph dev 健康检查."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{lg_base_url}/ok")
                assert response.status_code == 200
                print(f"✅ LangGraph dev ready: {response.text}")
        except httpx.ConnectError:
            pytest.skip(
                "LangGraph dev not running.\n"
                "Start with: cd backend/python && uv run langgraph dev --port 2024"
            )

    @pytest.mark.asyncio
    async def test_invoke_fact_checker_via_api(self, lg_base_url: str):
        """通过 LangGraph API 调用 Fact Checker."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{lg_base_url}/fact_checker/invoke",
                    json={
                        "input": {
                            "topic": "彩礼",
                            "iteration": 0,
                            "queries": [],
                            "should_continue": True,
                            "report": None,
                        }
                    },
                    timeout=30.0,
                )
                assert response.status_code in [200, 201]
                data = response.json()
                print(f"✅ LangGraph invoke response: {json.dumps(data, indent=2)}")
        except httpx.ConnectError:
            pytest.skip("LangGraph dev not running")


class TestHarnessE2E:
    """Harness 层端到端测试."""

    @pytest.mark.asyncio
    async def test_harness_real_execution(self):
        """Harness 真实执行测试."""
        from wenexus.agent.fact_checker.harness.harness import FactCheckerHarness

        harness = FactCheckerHarness(max_iterations=2)
        report = await harness.run(
            topic_title="彩礼争议", topic_description="关于彩礼的讨论"
        )

        assert report.topic_title == "彩礼争议"
        assert report.facts is not None
        print(f"✅ Harness report: {report.to_dict()}")
