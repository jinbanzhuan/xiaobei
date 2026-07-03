import os
import random
import sys
import time
import traceback
from typing import Any

import pytest
import requests
import urllib3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_client import base_url
from config.get_token import token
from config.logger import get_logger

urllib3.disable_warnings()


class TestChat:
    logger = get_logger()

    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    session = requests.Session()
    session.headers.update(headers)
    session.verify = False

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        step: str,
        expected_status: int = 200,
        **kwargs: Any,
    ) -> dict:
        """统一请求封装：检查 HTTP 状态码并返回 JSON。"""
        resp = self.session.request(
            method=method,
            url=url,
            timeout=kwargs.pop("timeout", (10, 30)),
            **kwargs,
        )

        assert resp.status_code == expected_status, (
            f"\n{step} 请求失败，HTTP 状态码错误: {resp.status_code}\n"
            f"URL: {url}\n"
            f"响应: {resp.text}"
        )

        try:
            body = resp.json()
        except ValueError as exc:
            raise AssertionError(
                f"\n{step} 响应不是合法 JSON\nURL: {url}\n响应: {resp.text}"
            ) from exc

        return body

    def _get_random_enterprise_id(self) -> str:
        """随机取一个企业 ID。"""
        body = self._request_json(
            "GET",
            f"{base_url}/api/v1/enterprises",
            step="[01] 获取企业列表",
            params={
                "pageSize": 100,
                "page": 1,
            },
            timeout=(5, 30),
        )

        enterprises = body.get("data", {}).get("list") or []
        assert enterprises, f"[01] 企业列表为空，响应: {body}"

        enterprise = random.choice(enterprises)
        enterprise_id = enterprise["id"]

        self.logger.info(
            f"[01] ✅ 获取随机企业成功: enterpriseId={enterprise_id}, "
            f"name={enterprise.get('name')}"
        )
        return enterprise_id

    def _create_visit(self, enterprise_id: str) -> str:
        """为企业新增走访，返回 visitId。"""
        body = self._request_json(
            "POST",
            f"{base_url}/api/v1/visits",
            step="[02] 新增走访",
            json={
                "enterpriseId": enterprise_id,
                "visitors": ["金阳"],
                "participants": [{"name": "金阳"}],
                "source": "手动录入",
            },
            timeout=(5, 30),
        )

        data = body.get("data") or {}
        assert data.get("enterpriseId") == enterprise_id, (
            f"\n[02] 企业 ID 不一致，"
            f"返回 enterpriseId={data.get('enterpriseId')}，"
            f"期望 enterpriseId={enterprise_id}，"
            f"完整响应: {body}"
        )

        visit_id = data.get("id")
        assert visit_id, f"[02] 新增走访响应里没有 id，响应: {body}"

        self.logger.info(f"[02] ✅ 新增走访成功: visitId={visit_id}")
        return visit_id

    def _invoke_xiaobei(self, visit_id: str, message: str) -> str:
        """调用小北，返回 taskId。"""
        body = self._request_json(
            "POST",
            f"{base_url}/api/v1/xiaobei/invoke",
            step="[03] 调用小北",
            json={
                "message": message,
                "visitId": visit_id,
            },
            timeout=(10, 30),
        )

        task_id = body.get("data", {}).get("taskId")
        assert task_id, f"[03] 响应中没有 taskId，响应: {body}"

        self.logger.info(f"[03] ✅ 触发小北任务成功: taskId={task_id}")
        return task_id

    def _wait_task_completed(
        self,
        task_id: str,
        *,
        interval_seconds: int = 2,
        max_wait_seconds: int = 300,
    ) -> dict:
        """轮询任务状态直到 completed / failed / canceled / 超时。"""
        deadline = time.time() + max_wait_seconds

        while time.time() < deadline:
            body = self._request_json(
                "GET",
                f"{base_url}/api/v1/tasks/{task_id}",
                step="[04] 查询任务结果",
                timeout=(10, 30),
            )

            data = body.get("data") or {}
            status = data.get("status", "")

            if status in ["", "pending", "processing"]:
                self.logger.info(f"[04] 👀 任务处理中: taskId={task_id}, status={status}")
                time.sleep(interval_seconds)
                continue

            if status in ["failed", "canceled"]:
                raise AssertionError(
                    f"[04] ☹️ 任务失败/取消: taskId={task_id}, "
                    f"status={status}, 完整响应: {body}"
                )

            if status == "completed":
                self.logger.info(
                    f"[04] ✅ 获取小北结果成功: taskId={task_id}, "
                    f"result={data.get('result', '')}"
                )
                return data

            raise AssertionError(
                f"[04] 未知任务状态: taskId={task_id}, status={status}, 完整响应: {body}"
            )

        raise TimeoutError(
            f"[04] 等待任务超时: taskId={task_id}, "
            f"max_wait_seconds={max_wait_seconds}"
        )

    @pytest.mark.manual
    def test_chat_smoke(self):
        """交互式小北 smoke 测试。

        说明：
        - 这个用例需要人工在终端输入消息。
        - 输入 q / quit / exit 可退出循环。
        - 如果要放进 CI，不建议使用 input()，应改成固定 message 参数化。
        """
        visits_id: list[str] = []
        enterprise_id: list[str] = []
        tasks_id: list[str] = []

        try:
            eid = self._get_random_enterprise_id()
            enterprise_id.append(eid)

            visit_id = self._create_visit(eid)
            visits_id.append(visit_id)

            while True:
                msg = input("🫧 小北输入框，输入 q 退出: ").strip()
                if msg.lower() in {"q", "quit", "exit"}:
                    self.logger.info("用户主动退出小北交互测试")
                    break

                if not msg:
                    self.logger.warning("输入为空，已跳过")
                    continue

                task_id = self._invoke_xiaobei(visit_id, msg)
                tasks_id.append(task_id)

                self._wait_task_completed(task_id)

        except Exception as e:
            self.logger.error(f"任务 list: {tasks_id}")
            self.logger.error(f"走访 list: {visits_id}")
            self.logger.error(f"企业 list: {enterprise_id}")
            self.logger.error(f"测试异常: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
            raise


if __name__ == "__main__":
    test = TestChat()
    test.test_chat_smoke()