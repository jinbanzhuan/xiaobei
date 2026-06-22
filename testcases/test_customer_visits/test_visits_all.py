from logging import exception
from sqlite3 import DataError

import pytest
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


class TestVisitsAll:
    r = random.randint(0, 99)
    # base_url = "https://dev-bo-api.xiaobei.top"
    # base_url = "http://localhost:12888/"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.走访smoke
    def test_visits_smoke(self):
        visits_id = []
        enterprise_id = []
        tasks_id = []
        feishu_url = "https://fcn6bo5q7kmm.feishu.cn/docx/HNNTdbNocojItcxLzf8cwZ7Enfh"
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                verify=False
            )
            assert get_enterprises.status_code == 200, f"\n[01]🙅获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"\n[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            print(f"\n[01]✅获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                verify=False
            )
            assert add_visits.status_code == 200, f"\n[02]🙅新增走访失败,️响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]🙅新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            print(f"[02]✅新增走访:{add_visits.json()['data']}")

            # ==================== [03]扭转状态checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                verify=False
            )
            assert checklists.status_code == 200, f"\n[03]🙅响应码错误:{checklists.status_code}"
            assert checklists.json()['data'][
                       'status'] == "checklist", f"\n[03]🙅状态非checklist,实际状态:{checklists.json()['data']['status']}"
            assert checklists.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[03]🙅企业id不一致,返回值enterpriseId:{checklists.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            print(f"[03]准备阶段-沟通清单:{checklists.json()['data']}")

            # ==================== [04]扭转状态visiting ====================
            visitings = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                verify=False
            )

            assert visitings.status_code == 200, f"\n[04]🙅响应码错误:{visitings.status_code}"
            assert visitings.json()['data'][
                       'status'] == "visiting", f"\n[04]🙅状态非checklist,实际状态:{visitings.json()['data']['status']}"
            assert visitings.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[04]🙅企业id不一致,返回值enterpriseId:{visitings.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            print(f"[04]✅准备阶段-走访中: {visitings.json()['data']}")

            # ==================== [05]扭转状态confirmed ====================
            confirmed = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "confirmed"
                },
                headers=self.headers,
                verify=False
            )

            assert confirmed.status_code == 200, f"\n[05]🙅响应码错误:{confirmed.status_code}"
            assert confirmed.json()['data'][
                       'status'] == "confirmed", f"\n[05]🙅状态非checklist,实际状态:{confirmed.json()['data']['status']}"
            assert confirmed.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[05]🙅企业id不一致,返回值enterpriseId:{confirmed.json()['data']['enterpriseId']},列表enterpriseId:{enterprise_id[0]}"
            print(f"[05]✅结束阶段-记录走访要点:{confirmed.json()['data']}")

            # ==================== [06]上传走访材料成功 ====================
            add_attachments = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/attachments",
                json={
                    "type": "url",
                    "url": feishu_url,
                    "name": "飞书妙记"
                },
                headers=self.headers,
                verify=False
            )
            # 断言状态码和响应结果
            assert add_attachments.status_code == 200, f"\n[06]🙅响应码错误:{add_attachments.status_code}"
            assert add_attachments.json()['data'][
                       'url'] == feishu_url, f"[06]🙅上传材料url错误,返回值:{add_attachments.json()['data']['url']},列表url:{feishu_url}"
            print(f"[06]✅上传走访材料成功:{add_attachments.json()['data']}")

            # ==================== [07]贴妙记/文档/智能纪要,拉内容写进visit ====================
            add_parse = requests.post(
                url=f"{base_url}/api/v1/minutes/parse",
                json={
                    "enterpriseId": enterprise_id[0],
                    "visitId": visits_id[0],
                    "rawContent": feishu_url
                },
                headers=self.headers,
                verify=False
            )
            assert add_parse.status_code == 200, f"\n[07]🙅响应码错误:{add_parse.status_code}"
            assert add_parse.json()['data']['taskId'] is not None, f"\n[07]🙅tasksId为空, 返回值:{add_parse.json()}"
            tasks_id.append(add_parse.json()['data']['taskId'])
            print(f"[07]✅内容写入visits成功:{add_parse.json()['data']}")

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
                    verify=False
                )
                assert parse_result.status_code == 200, f"\n[08]🙅响应码错误:{parse_result.status_code}"
                assert parse_result.json()['status'] in ["", "pending", "processing", "completed", "failed",
                                                         "canceled"], f"\n[08]🙅状态不对,返回值:{parse_result.json()}"
                if parse_result.json()['status'] in ["", "pending", "processing"]:
                    time.sleep(2)
                elif parse_result.json()['status'] == "failed":
                    pytest.fail(f"\n[08]🙅解析结果查询失败:{parse_result.json()}")
                elif parse_result.json()["status"] == "canceled":
                    pytest.fail(f"[08]🙅任务被取消:{parse_result.json()}")
                elif parse_result.json()['status'] == "completed":
                    print(f"[08]✅轮询第 {j + 1} 次解析结果成功{parse_result.json()['status']}")
                    break
                else:
                    print(f"\n[08]☕️AI 分析任务 3 分钟未完成:{parse_result.json()}")

            # ===================== [09]触发ai分析 ====================
            add_analyze = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/analyze",
                json={},
                headers=self.headers,
                verify=False
            )
            assert add_analyze.status_code == 200, f"\n[09]🙅响应码错误:{add_analyze.status_code}"
            tasks_id.append(add_analyze.json()['data']['taskId'])
            print(f"[09]✅触发ai分析成功:{add_analyze.json()['data']}")

            # ===================== [10]查询解析结果 status==processing ====================
            """
            pending	    任务已创建，还没被 worker 消费	继续轮询
            processing	worker 正在解析妙记、拉转写、写 visit	继续轮询
            completed	妙记解析完成，已写入 visits.raw_minutes_content 等字段	可以继续调用 /api/v1/visits/{visitId}/analyze
            failed	    妙记解析失败，比如权限不足、链接无效、转写不可读、查重等	直接失败，打印 error
            canceled	任务被取消，通常是同一个 visit 又发起了新的 parse，旧任务被 supersede
            """
            for i in range(60):
                get_tasks = requests.get(
                    url=f"{base_url}/api/v1/minutes/parsed/{tasks_id[1]}",
                    headers=self.headers,
                    verify=False
                )
                assert get_tasks.status_code == 200, f"\n[10]🙅响应码错误:{get_tasks.status_code}"
                assert get_tasks.json()['data']['status'] in ["", "pending", "processing", "completed", "failed",
                                                              "canceled"], f"\n[08]🙅状态不对,返回值:{get_tasks.json()}"
                if get_tasks.json()["data"]["status"] in ["", "pending", "processing"] or get_tasks.json()["data"][
                    "status"] == "pending":
                    time.sleep(2)
                elif get_tasks.json()["data"]["status"] == "failed":
                    pytest.fail(f"\n[10]🙅解析结果查询失败:{get_tasks.json()}")
                elif get_tasks.json()["data"]["status"] == "canceled":
                    pytest.fail(f"[10]🙅任务被取消:{get_tasks.json()['data']}")
                elif get_tasks.json()["data"]["status"] == "completed":
                    print(f"[10]✅轮询第 {i + 1} 次获取任务结果成功:{get_tasks.json()['data']}")
                    break
                else:
                    print(f"[10]☕️AI 分析任务 10 分钟未完成{get_tasks.json()["data"]}")

            # ===================== [11]AI提取画像更新 ====================
            add_profile_updates = requests.get(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/profile-updates",
                headers=self.headers,
                verify=False
            )
            # 断言状态码和响应结果
            assert add_profile_updates.status_code == 200, f"\n[10]🙅响应码错误:{add_profile_updates.status_code}"
            assert add_profile_updates.json()['data']['visitId'] == visits_id[
                0], f"\n[10]🙅画像更新visitId错误,返回值:{add_profile_updates.json()['data']['visitId']},列表visitId:{visits_id[0]}"
            print(f"[11]✅AI提取的画像更新成功:{add_profile_updates.json()['data']}")

            # ===================== [12]提交走访 ====================
            add_submit = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/submit",
                json={},
                headers=self.headers,
                verify=False
            )
            assert add_submit.status_code == 200, f"\n[12]🙅响应码错误:{add_submit.status_code}"
            assert add_submit.json()['data']['visitId'] == visits_id[
                0], f"\n[12]🙅提交走访visitId错误,返回值:{add_submit.json()['data']['visitId']},列表visitId:{visits_id[0]}"
            print(f"[12]✅提交走访成功:{add_submit.json()['data']}")

            # ===================== [13]扭转状态submitted ====================
            commit_visits = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={"status": "submitted"},
                headers=self.headers,
                verify=False
            )
            # 断言状态码和响应结果
            assert commit_visits.status_code == 200, f"\n[13]🙅响应码错误:{commit_visits.status_code}"
            assert commit_visits.json()['data'][
                       'status'] == "submitted", f"\n[13]🙅状态错误,返回值:{commit_visits.json()['data']['status']}"
            print(f"[13]✅跟进阶段-需求处理与任务分配:{commit_visits.json()['data']}")

            # ==================== [14]删除走访 ====================
            del_response = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                verify=False
            )
            assert del_response.status_code == 200, f"\n[14]🙅响应码错误:{del_response.status_code}"
            assert del_response.json()['code'] == 0, f"\n[14]🙅删除走访失败,返回值:{del_response.json()}"
            print(f"[14]✅太🐂了, 冒烟测试成功👍, 辛苦啦💦:{del_response.json()}\n")

        except AssertionError:
            print(f"\n❌ 断言错误 ❌")
            traceback.print_exc()
        except IndexError:
            print(f"❌ 索引错误 ❌")
            traceback.print_exc()
        except Exception as e:
            print(f"❌ 未知错误 ❌:{e}")
            traceback.print_exc()

    @pytest.mark.准备阶段_删除走访
    def test_add_visits_case(self):
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                verify=False
            )

            assert get_enterprises.status_code == 200, f"\n[01]☣️获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"\n[01]☣️add随机企业id失败,列表为空:{enterprise_id}"
            print(f"\n[01]✅获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                verify=False
            )
            assert add_visits.status_code == 200, f"\n[02]☣️新增走访失败,️响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]☣️新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            print(f"[02]✅新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                verify=False
            )
            assert del_visits.status_code == 200, f"\n[03]☣️删除走访失败,️响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"\n[03]☣️删除走访失败:{del_visits.json()}"
            print(f"[04]✅删除走访成功:{del_visits.json()}\n")

        except AssertionError:
            print(f"\n❌ 断言错误 ❌")
            traceback.print_exc()
        except IndexError:
            print(f"❌ 索引错误 ❌")
            traceback.print_exc()
        except DataError:
            print(f"❌ 数据错误 ❌")
            traceback.print_exc()
        except Exception as e:
            print(f"❌ 未知错误 ❌:{e}")
            traceback.print_exc()

    @pytest.mark.走访阶段_删除走访
    def test_del_ready_visits_case(self):
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                verify=False
            )

            assert get_enterprises.status_code == 200, f"\n[01]☣️获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"\n[01]☣️add随机企业id失败,列表为空:{enterprise_id}"
            print(f"\n[01]✅获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                verify=False
            )
            assert add_visits.status_code == 200, f"\n[02]☣️新增走访失败,响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]☣️新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            visits_id.append(add_visits.json()['data']['id'])
            print(f"[02]✅新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]扭转状态checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                verify=False
            )
            assert checklists.status_code == 200, f"\n[03]☣️扭转状态checklist失败,响应码错误:{checklists.status_code}"
            assert checklists.json()['data'][
                       'status'] == "checklist", f"\n[03]☣️扭转状态checklist失败:{checklists.json()}"
            assert checklists.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]☣️企业id不一致,返回值enterpriseId:{checklists.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            print(f"[03]✅扭转状态为:{checklists.json()['data']['status']}")

            # ==================== [04]扭转状态visitings ====================
            visitings = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                verify=False
            )
            assert visitings.status_code == 200, f"\n[03]☣️扭转状态visitings失败,响应码错误:{visitings.status_code}"
            assert visitings.json()['data']['status'] == "visiting", f"\n[03]☣️扭转状态checklist失败:{visitings.json()}"
            assert visitings.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]☣️企业id不一致,返回值enterpriseId:{visitings.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            print(f"[04]✅扭转状态为:{visitings.json()['data']['status']},跳转到 走访阶段")

            # ==================== [05]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                verify=False
            )
            assert del_visits.status_code == 200, f"\n[03]☣️删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"\n[03]☣️删除走访失败:{del_visits.json()}"
            print(f"[04]✅删除走访成功:{del_visits.json()}\n")

        except AssertionError:
            print(f"\n❌ 断言错误 ❌")
            traceback.print_exc()
        except IndexError:
            print(f"❌ 索引错误 ❌")
            traceback.print_exc()
        except Exception as e:
            print(f"❌ 未知错误 ❌:{e}")
            traceback.print_exc()

    @pytest.mark.删除隐藏走访
    def test_del_hidden_visits_case(self):
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                verify=False
            )
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert get_enterprises.status_code == 200, f"\n[01]☣️获取随机企业失败,响应码错误:{get_enterprises.status_code}"
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"\n[01]☣️add随机企业id失败,列表为空:{enterprise_id}"
            print(f"\n[01]✅获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                verify=False
            )
            assert add_visits.status_code == 200, f"\n[02]☣️新增走访失败,响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"\n[02]☣️企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            print(f"[02]✅新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]隐藏走访 ====================
            hide = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/hide",
                json={"hidden": True},
                headers=self.headers,
                verify=False
            )
            assert hide.status_code == 200, f"\n[03]☣️隐藏走访失败,响应码错误:{hide.status_code}"
            assert hide.json()['data']['hidden'] == True, f"\n[03]☣️返回值不是True,实际返回值:{hide.json()}"
            print(f"[03]✅隐藏走访成功:{hide.json()['data']['hidden']}")

            # ==================== [04]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                verify=False
            )
            assert del_visits.status_code == 200, f"\n[03]☣️删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"\n[03]☣️删除走访失败:{del_visits.json()}"
            print(f"[04]✅删除走访成功:{del_visits.json()}\n")

        except AssertionError:
            print(f"\n❌ 断言错误 ❌")
            traceback.print_exc()
        except IndexError:
            print(f"\n❌ 索引错误 ❌")
            traceback.print_exc()
        except Exception as e:
            print(f"\n❌ 未知错误 ❌:{e}")
            traceback.print_exc()

    @pytest.mark.提交走访
    def test_submit_visits_case(self):
        print()

    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
