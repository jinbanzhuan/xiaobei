import pytest
import requests
import random
import traceback
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_client import BASE_URL
from config.get_token import TOKEN
import urllib3

urllib3.disable_warnings()

"""
新增走访
POST/api/v1/visits
enterpriseId	    string	    ✅	企业 ID
visitors        	string[]	✅	我方参会人姓名
participants	    object[]	❌	结构化参会人 { name, userId?, openId? }
department	        string	    ❌	所属部门
keyPoints	        string[]	❌	走访要点
enterpriseDemands	string[]	❌	企业需求
followUpItems	    string[]	❌	跟进事项
source	            string	    ❌	来源，默认 手动录入
minutesId	        string	    ❌	飞书妙记 ID

上传走访材料
POST /api/v1/visits/{visitId}/attachments
visitId (path)	 string	✅	走访 ID
type	         string	✅	file / link / text
name	         string	❌	显示名
url 	         string	❌	type=file/link 时填
content	         string	❌	type=text 时填正文
fileSize	     int64	❌	type=file 时填
mimeType	     string	❌	type=file 时填

触发 AI 分析
POST /api/v1/visits/{visitId}/analyze
visitId (path)	string	✅	走访 ID

轮询 pending profile updates
GET /api/v1/visits/{visitId}/profile-updates
visitId (path)	string	✅	走访 ID

提交走访（应用画像更新）
POST /api/v1/visits/{visitId}/submit
visitId (path)	    string	    ✅	走访 ID
applyProfileKeys	string[]	❌	要应用的字段 key；空数组/不传 = 应用全部 pending

走访列表
GET/api/v1/visits
走访详情
GET/api/v1/visits/{visitId}
编辑走访
PUT/api/v1/visits/{visitId}
删除走访
DELETE/api/v1/visits/{visitId}
隐藏走访
POST/api/v1/visits/{visitId}/hide
"""


class TestVisitsAll:
    visits_id = []
    enterprise_id = []
    tasks_id = []
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    @pytest.mark.走访smoke
    def test_visits_all(self):
        try:
            # ==================== [01/13]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{BASE_URL}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                verify=False
            )
            self.enterprise_id.append(get_enterprises.json()['data']['list'][
                                          random.randint(0, len(get_enterprises.json()['data']['list']) - 1)]['id'])

            # ==================== [02/13]新增走访 ====================
            add_visits = requests.post(
                url=f"{BASE_URL}/api/v1/visits",
                json={
                    "enterpriseId": self.enterprise_id[0],
                    "visitors": ["金阳"],
                    "participants": [{"name": "金阳"}],
                    "source": "手动录入"
                },
                headers=self.headers,
                verify=False
            )
            assert add_visits.status_code == 200
            assert add_visits.json()['data']['enterpriseId'] == self.enterprise_id[0]

            # 添加新增的走访id到class类列表
            self.visits_id.append(add_visits.json()['data']['id'])
            # self.enterprise_id.append(add_visits.json()['data']['enterpriseId'])

            # ==================== [03/13]扭转状态checklist ====================
            checklists = requests.put(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                verify=False
            )
            assert checklists.status_code == 200
            assert checklists.json()['data']['status'] == "checklist"
            assert checklists.json()['data']['enterpriseId'] == self.enterprise_id[0]

            # ==================== [04/13]扭转状态visiting ====================
            visitings = requests.put(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                verify=False
            )
            assert visitings.status_code == 200
            assert visitings.json()['data']['status'] == "visiting"
            assert visitings.json()['data']['enterpriseId'] == self.enterprise_id[0]

            # ==================== [05/13]扭转状态confirmed ====================
            confirmed = requests.put(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
                json={
                    "status": "confirmed"
                },
                headers=self.headers,
                verify=False
            )
            assert confirmed.status_code == 200
            assert confirmed.json()['data']['status'] == "confirmed"
            assert confirmed.json()['data']['enterpriseId'] == self.enterprise_id[0]

            # ==================== [06/13]上传走访材料成功 ====================
            add_attachments = requests.post(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/attachments",
                json={
                    "type": "url",
                    "url": "https://fcn6bo5q7kmm.feishu.cn/minutes/obcnwganei6q1558sd4m59o1",
                    "name": "飞书妙记"
                },
                headers=self.headers,
                verify=False
            )
            assert add_attachments.status_code == 200

            # ==================== [07/13]贴妙记/文档/智能纪要,拉内容写进visit ====================
            add_parse = requests.post(
                url=f"{BASE_URL}/api/v1/minutes/parse",
                json={
                    "enterpriseId": self.enterprise_id[0],
                    "visitId": self.visits_id[0],
                    "rawContent": "https://fcn6bo5q7kmm.feishu.cn/minutes/obcnwganei6q1558sd4m59o1"
                },
                headers=self.headers,
                verify=False
            )
            self.tasks_id.append(add_parse.json()['data']['taskId'])
            assert add_parse.status_code == 200

            # ===================== [07.1/13]轮询妙记解析任务结果 ====================
            for j in range(90):  # 90 * 2s = 约 3 分钟
                get_parse_result = requests.get(
                    url=f"{BASE_URL}/api/v1/minutes/parse-result/{self.tasks_id[0]}",
                    headers=self.headers,
                    verify=False
                )
                parse_result = get_parse_result.json()["status"]

                if parse_result == "completed":
                    break
                elif parse_result == "failed":
                    pytest.fail(f"妙记解析失败")
                elif parse_result == "canceled":
                    pytest.fail(f"妙记解析任务被取消")
                time.sleep(2)
            else:
                pytest.fail("妙记解析任务 3 分钟未完成")

            # ===================== [08/13]触发ai分析 ====================
            add_analyze = requests.post(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/analyze",
                json={},
                headers=self.headers,
                verify=False
            )
            assert add_analyze.status_code == 200
            self.tasks_id.append(add_analyze.json()['data']['taskId'])

           # ===================== [09/13]轮询status==completed ====================
            for i in range(60):
                get_tasks = requests.get(
                    url=f"{BASE_URL}/api/v1/minutes/parsed/{self.tasks_id[1]}",
                    headers=self.headers,
                    verify=False
                )
                ai_summary = get_tasks.json()["data"]["visitRecord"]["aiSummary"]
                if ai_summary == "" and get_tasks.status_code == 200:
                    time.sleep(10)
                elif ai_summary != "" and get_tasks.status_code == 200:
                    break
            else:
                pytest.fail("AI 分析任务 10 分钟未完成")

           # ===================== [10/13]AI提取的画像更新 ====================
            add_profile_updates = requests.get(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/profile-updates",
                headers=self.headers,
                verify=False
            )
            # 断言状态码和响应结果
            assert add_profile_updates.status_code == 200
            assert add_profile_updates.json()['data']['visitId'] == self.visits_id[0]

            # ===================== [11/13]画像更新落库到企业 ====================
            add_submit = requests.post(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/submit",
                json={},
                headers=self.headers,
                verify=False
            )
            assert add_submit.status_code == 200
            assert add_submit.json()['data']['visitId'] == self.visits_id[0]

            # ===================== [12/13]扭转状态submitted ====================
            commit_visits = requests.put(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
                json={"status": "submitted"},
                headers=self.headers,
                verify=False
            )
            # 断言状态码和响应结果
            assert commit_visits.status_code == 200
            assert commit_visits.json()['data']['status'] == "submitted"

            # ==================== [13/13]删除走访 ====================
            del_response = requests.delete(
                url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
                headers=self.headers,
                verify=False
            )
            assert del_response.status_code == 200
            assert del_response.json()['code'] == 0

        except AssertionError:
            print(f"\n❌断言错误❌")
            traceback.print_exc()
        except IndexError:
            print(f"\n❌索引错误❌")
            traceback.print_exc()
        except Exception:
            print(f"\n❌未知错误❌:{Exception}")
            traceback.print_exc()
        else:
            print(
                f"\n[01/13]✅获取随机企业id:{get_enterprises.json()['data']['list'][random.randint(0, len(get_enterprises.json()['data']['list']) - 1)]['id']}")
            print(f"[02/13]✅新增走访:{add_visits.json()['data']['createdAt']}")
            print(f"[03/13]✅准备阶段-沟通清单:{checklists.json()['data']['status']}")
            print(f"[04/12]✅准备阶段-走访中:{visitings.json()['data']['status']}")
            print(f"[05/13]✅结束阶段-记录走访要点:{confirmed.json()['data']['status']}")
            print(f"[06/13]✅上传走访材料成功:{add_attachments.json()['data']['url']}")
            print(f"[07/13]✅写入走访内容到visits成功:{add_parse.json()['data']}")
            print(f"[07.1/13]✅轮询第 {j + 1} 次妙记解析完成:{get_parse_result.json()['status']}")
            print(f"[08/13]✅触发AI分析成功:{add_analyze.json()['data']}")
            print(f"[09/13]✅轮询第 {i + 1} 次获取任务结果成功:{get_tasks.json()['data']['visitRecord']['aiSummary']}")
            print(f"[10/13]✅AI提取的画像更新成功:{add_profile_updates.json()['data']['items']}") # [0]['newValue']
            print(f"[11/13]✅提交走访成功:{add_submit.json()}")
            print(f"[12/13]✅跟进阶段-需求处理与任务分配:{commit_visits.json()['data']['status']}")
            print(f"[13/13]✅冒烟测试成功👍,辛苦啦💦:{del_response.json()}")
            print(f"\n[1/3]📊对比走访id:{self.visits_id}")
            print(f"[2/3]📊对比企业id:{self.enterprise_id}")
            print(f"[3/3]📊对比任务id:{self.tasks_id}")




    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
