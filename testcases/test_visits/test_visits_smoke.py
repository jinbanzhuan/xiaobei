import pytest
import requests
import random
import traceback
import time
import urllib3

urllib3.disable_warnings()
from config.get_token import token
from config.api_client import base_url
from utils.logger import get_logger

"""
测试case:
01, 整个走访smoke case
02, 
03, 
04, 
05, 
06, 
07, 
"""

class TestVisitsSmoke:
    logger = get_logger()
    r = random.randint(0, 99)
    # base_url = "https://dev-bo-api.xiaobei.top"
    # base_url = "http://localhost:12888/"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.smoke
    def test_visits_smoke(self):
        visits_id = []
        enterprise_id = []
        tasks_id = []
        feishu_url = "https://fcn6bo5q7kmm.feishu.cn/minutes/obcnn93hqjwgf17o1l6x4ys8"
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01]✅获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02]新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id[0],
                    "visitors": ["金阳"],
                    "participants": [{"name": "金阳"}],
                    "source": "手动录入"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert add_visits.status_code == 200, f"[02]🙅新增走访失败,️响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]🙅新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            self.logger.info(f"[02]✅新增走访:{add_visits.json()}")

            # ==================== [03]扭转状态 checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert checklists.status_code == 200, f"[03]🙅响应码错误:{checklists.status_code}"
            assert checklists.json()['data'][
                       'status'] == "checklist", f"[03]🙅状态非checklist,实际状态:{checklists.json()['data']['status']}"
            assert checklists.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[03]🙅企业id不一致,返回值enterpriseId:{checklists.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            self.logger.info(f"[03]✅准备阶段-沟通清单:{checklists.json()}")

            # ==================== [04]扭转状态 visiting ====================
            visitings = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )

            assert visitings.status_code == 200, f"[04]🙅响应码错误:{visitings.status_code}"
            assert visitings.json()['data'][
                       'status'] == "visiting", f"[04]🙅状态非checklist,实际状态:{visitings.json()['data']['status']}"
            assert visitings.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[04]🙅企业id不一致,返回值enterpriseId:{visitings.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            self.logger.info(f"[04]✅准备阶段-走访中: {visitings.json()}")

            # ==================== [05]扭转状态 confirmed ====================
            confirmed = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "confirmed"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )

            assert confirmed.status_code == 200, f"[05]🙅响应码错误:{confirmed.status_code}"
            assert confirmed.json()['data'][
                       'status'] == "confirmed", f"[05]🙅状态非checklist,实际状态:{confirmed.json()['data']['status']}"
            assert confirmed.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[05]🙅企业id不一致,返回值enterpriseId:{confirmed.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            self.logger.info(f"[05]✅结束阶段-记录走访要点:{confirmed.json()}")

            # ==================== [06]上传走访材料成功 ====================
            add_attachments = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/attachments",
                json={
                    "type": "url",
                    "url": feishu_url,
                    "name": "飞书妙记"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和响应结果
            assert add_attachments.status_code == 200, f"[06]🙅响应码错误:{add_attachments.status_code}"
            assert add_attachments.json()['data'][
                       'url'] == feishu_url, f"[06]🙅上传材料url错误,返回值:{add_attachments.json()['data']['url']},列表url:{feishu_url}"
            self.logger.info(f"[06]✅上传走访材料成功:{add_attachments.json()}")

            # ==================== [07]贴妙记/文档/智能纪要,拉内容写进visit ====================
            add_parse = requests.post(
                url=f"{base_url}/api/v1/minutes/parse",
                json={
                    "enterpriseId": enterprise_id[0],
                    "visitId": visits_id[0],
                    "rawContent": feishu_url
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert add_parse.status_code == 200, f"[07]🙅响应码错误:{add_parse.status_code}"
            assert add_parse.json()['data']['taskId'] is not None, f"[07]🙅tasksId为空, 返回值:{add_parse.json()}"
            tasks_id.append(add_parse.json()['data']['taskId'])
            self.logger.info(f"[07]✅内容写入visits成功:{add_parse.json()}")

            # ===================== [08]查询解析结果 status==completed ====================
            """
            pending	    任务已创建，还没被 worker 消费	继续轮询
            processing	worker 正在解析妙记、拉转写、写 visit	继续轮询
            completed	妙记解析完成，已写入 visits.raw_minutes_content 等字段	可以继续调用 /api/v1/visits/{visitId}/analyze
            failed	    妙记解析失败，比如权限不足、链接无效、转写不可读、查重等	直接失败，打印 error
            canceled	任务被取消，通常是同一个 visit 又发起了新的 parse，旧任务被 supersede
            """
            for j in range(90):
                parse_result = requests.get(
                    url=f"{base_url}/api/v1/minutes/parse-result/{tasks_id[0]}",
                    headers=self.headers,
                    timeout=(30, 60),
                    verify=False
                )
                assert parse_result.status_code == 200, f"[08]🙅响应码错误:{parse_result.status_code}"

                if parse_result.json()['status'] in ["", "pending", "processing"]:
                    time.sleep(2)
                elif parse_result.json()['status'] == "failed":
                    pytest.fail(f"[08]🙅解析结果查询失败:{parse_result.json()}")
                elif parse_result.json()["status"] == "canceled":
                    pytest.fail(f"[08]🙅任务被取消:{parse_result.json()}")
                elif parse_result.json()['status'] == "completed":
                    self.logger.info(f"[08]✅轮询第 {j + 1} 次解析结果成功:{parse_result.json()['status']}")
                    break
                else:
                    self.logger.info(f"[08]☕️AI 分析任务 3 分钟未完成:{parse_result.json()}")

            # ===================== [09]触发ai分析 ====================
            add_analyze = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/analyze",
                json={},
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert add_analyze.status_code == 200, f"[09]🙅响应码错误:{add_analyze.status_code}"
            tasks_id.append(add_analyze.json()['data']['taskId'])
            self.logger.info(f"[09]✅触发ai分析成功:{add_analyze.json()}")

            # ===================== [10]查询解析结果 status==processing ====================
            """
            pending	    任务已创建，还没被 worker 消费	继续轮询
            processing	worker 正在解析妙记、拉转写、写 visit	继续轮询
            completed	妙记解析完成，已写入 visits.raw_minutes_content 等字段	可以继续调用 /api/v1/visits/{visitId}/analyze
            failed	    妙记解析失败，比如权限不足、链接无效、转写不可读、查重等	直接失败，打印 error
            canceled	任务被取消，通常是同一个 visit 又发起了新的 parse，旧任务被 supersede
            """
            i = 0
            while True:
                i += 1
                get_tasks = requests.get(
                    url=f"{base_url}/api/v1/minutes/parsed/{tasks_id[1]}",
                    headers=self.headers,
                    timeout=(30, 60),
                    verify=False
                )
                assert get_tasks.status_code == 200, f"[10]🙅响应码错误:{get_tasks.status_code}"
                assert get_tasks.json()['data']['status'] in ["", "pending", "processing", "completed", "failed",
                                                              "canceled"], f"[08]🙅状态不对,返回值:{get_tasks.json()}"
                if get_tasks.json()["data"]["status"] in ["", "pending", "processing"] or get_tasks.json()["data"][
                    "status"] == "pending":
                    time.sleep(2)
                elif get_tasks.json()["data"]["status"] == "failed":
                    pytest.fail(f"[10]🙅解析结果查询失败:{get_tasks.json()}")
                elif get_tasks.json()["data"]["status"] == "canceled":
                    pytest.fail(f"[10]🙅任务被取消:{get_tasks.json()['data']}")
                elif get_tasks.json()["data"]["status"] == "completed":
                    self.logger.info(f"[10]✅轮询第 {i + 1} 次获取任务结果成功:{get_tasks.json()['data']}")
                    break
                else:
                    self.logger.info(f"[10]☕️AI 分析任务 10 分钟未完成{get_tasks.json()}")

            # ===================== [11]AI提取画像更新 ====================
            add_profile_updates = requests.get(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/profile-updates",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和响应结果
            assert add_profile_updates.status_code == 200, f"[10]🙅响应码错误:{add_profile_updates.status_code}"
            assert add_profile_updates.json()['data']['visitId'] == visits_id[
                0], f"[10]🙅画像更新visitId错误,返回值:{add_profile_updates.json()['data']['visitId']},列表visitId:{visits_id[0]}"
            self.logger.info(f"[11]✅AI提取的画像更新成功:{add_profile_updates.json()}")

            # ===================== [12]提交走访 ====================
            add_submit = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/submit",
                json={},
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert add_submit.status_code == 200, f"[12]🙅响应码错误:{add_submit.status_code}"
            assert add_submit.json()['data']['visitId'] == visits_id[
                0], f"[12]🙅提交走访visitId错误,返回值:{add_submit.json()['data']['visitId']},列表visitId:{visits_id[0]}"
            self.logger.info(f"[12]✅提交走访成功:{add_submit.json()}")

            # ===================== [13]扭转状态 submitted ====================
            commit_visits = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={"status": "submitted"},
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和响应结果
            assert commit_visits.status_code == 200, f"[13]🙅响应码错误:{commit_visits.status_code}"
            assert commit_visits.json()['data'][
                       'status'] == "submitted", f"[13]🙅状态错误,返回值:{commit_visits.json()['data']['status']}"
            self.logger.info(f"[13]✅跟进阶段-需求处理与任务分配:{commit_visits.json()}")

            # # ==================== [14]删除走访 ====================
            del_response = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            assert del_response.status_code == 200, f"[14]🙅响应码错误:{del_response.status_code}"
            assert del_response.json()['code'] == 0, f"[14]🙅删除走访失败,返回值:{del_response.json()}"
            self.logger.info(f"[14]✅太 🐂 了, 冒烟测试成功 👍, 辛苦啦 💦:{del_response.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
