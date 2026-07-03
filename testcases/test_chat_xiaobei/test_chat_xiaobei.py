import requests
import random
import traceback
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.get_token import token
from config.api_client import base_url
import urllib3

urllib3.disable_warnings()
from config.logger import get_logger


class TestChat:
    logger = get_logger()
    r = random.randint(0, 99)
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    def test_chat_smoke(self):

        try:
            # ==================== [01]获取指定企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(5, 30),
                verify=False
            )
            assert get_enterprises.status_code == 200, f"[01] 🔍 获取随机企业id失败,️响应码错误: {get_enterprises.status_code}"
            self.logger.info(f"[01] ✅ 获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")
            enterprise_id = get_enterprises.json()['data']['list'][self.r]['id']

            # ==================== [02]新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id,
                    "visitors": ["金阳"],
                    "participants": [{"name": "金阳"}],
                    "source": "手动录入"
                },
                headers=self.headers,
                timeout=(5, 30),
                verify=False
            )
            assert add_visits.status_code == 200, f"\n[02] 🙅 新增走访失败,响应码错误: {add_visits.status_code}"
            visits_id = add_visits.json()['data']['id']
            self.logger.info(f"[02] ✅ 新增走访成功: {add_visits.json()}")

            # ==================== [03]无限循环王 ====================

            while True:
                msg = input(f"🫧小北输入框: ")
                msg_list = [msg]
                # ==================== [04]传参msg, 获取taskId ====================
                get_checklist = requests.post(
                    url=f"{base_url}/api/v1/xiaobei/invoke",
                    headers=self.headers,
                    json={
                        "message": msg,
                        "visitId": visits_id
                    },
                    timeout=(10, 30),
                    verify=False
                )
                assert get_checklist.status_code == 200, f"\n[03] 🔍 获取taskId失败,响应码错误: {get_checklist.status_code}"
                self.logger.info(f"[03] ✅ 触发checklist生成,获取taskId: {get_checklist.json()}")
                task_id = get_checklist.json().get('data', {}).get('taskId')

                # ==================== [04] 查询分析结果 ====================
                while True:
                    get_analysis = requests.get(
                        url=f"{base_url}/api/v1/tasks/{task_id}",
                        headers=self.headers,
                        timeout=(10, 30),
                        verify=False
                    )
                    if get_analysis.json().get('data', {}).get('status') in ["", "pending", "processing"]:
                        self.logger.info(f"[04] 👀 查询中...状态: {get_analysis.json().get('data', {}).get('status')}")
                        time.sleep(2)
                    elif get_analysis.json().get('data', {}).get('status') in ["failed", "canceled"]:
                        self.logger.error(f"[04] ☹️ 分析失败/任务取消: {get_analysis.json()}")
                        break
                    elif get_analysis.json().get('data', {}).get('status') == "completed":
                        result = get_analysis.json().get('data', {}).get('result', '')
                        self.logger.info(f"[04] 🤖 小贝: {result}\n")
                        break
                    else:
                        self.logger.error(f"[04] 🙅 未知状态: {get_analysis.json()}")

        except Exception as e:
            self.logger.error(f"测试异常: {e}")
            self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
            raise

if __name__ == "__main__":
    test = TestChat()
    test.test_chat_smoke()
