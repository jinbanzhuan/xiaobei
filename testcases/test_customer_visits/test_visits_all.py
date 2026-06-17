import pytest
import requests
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import BASE_URL
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
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    def test_add_visits(self):
        """
        测试用例：
        1. 新增走访
        """
        # POST /api/v1/visits
        add_visits = requests.post(
            url=f"{BASE_URL}/api/v1/visits",
            json={
                "enterpriseId": "7e367d34-ab10-41a6-b682-fc696bc76c63",
                "visitors": ["金阳"],
                "participants": [{"name": "金阳"}],
                "source": "手动录入"
            },
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert add_visits.status_code == 200
        assert add_visits.json()['data']['source'] is not None
        # 添加新增的走访id/企业id到class
        self.visits_id.append(add_visits.json()['data']['id'])
        self.enterprise_id.append(add_visits.json()['data']['enterpriseId'])
        # 响应结果
        print(f"\n[1/5]背调报告:{add_visits.json()}")

    def test_communication_checklist(self):
        """
        测试用例：
        1. 提交走访到"沟通清单",状态变更"checklist"页面在 准备阶段
        """
        # PUT /api/v1/visits/{visits_id}
        checklists = requests.put(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
            json={
                "status": "checklist"
            },
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert checklists.status_code == 200
        assert checklists.json()['data']['status'] == "checklist"
        # 响应结果
        print(f"\n[2/5]沟通清单:{checklists.json()}")

    def test_in_the_visits(self):
        """
        1,提交到"走访中"，状态变更"visiting"，页面刷新到 走访阶段
        """
        # PUT /api/v1/visits/{visits_id}
        communication_checklist = requests.put(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
            json={
                "status": "visiting"
            },
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert communication_checklist.status_code == 200
        assert communication_checklist.json()['data']['status'] == "visiting"
        # 响应结果
        print(f"\n[3/5]走访中:{communication_checklist.json()}")

    def test_record_visit_highlights(self):
        """
        1,提交到"记录走访要点"，状态变更"confirmed"，页面刷新到 结束阶段
        """
        # PUT /api/v1/visits/{visits_id}
        visit_highlights = requests.put(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
            json={
                "status": "confirmed"
            },
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert visit_highlights.status_code == 200
        assert visit_highlights.json()['data']['status'] == "confirmed"
        # 响应结果
        print(f"\n[4/5]走访中:{visit_highlights.json()}")

    def test_attachments(self):
        """
        1,上传走访材料
        """
        # post /api/v1/visits/{visitId}/attachments
        add_attachments = requests.post(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/attachments",
            json={
                "type": "url",
                "url": "https://fcn6bo5q7kmm.feishu.cn/docx/HNNTdbNocojItcxLzf8cwZ7Enfh",
                "name": "飞书妙记"
            },
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert add_attachments.status_code == 200
        # assert add_attachments.json()['data']['type'] == "url"
        # 响应结果
        print(f"\n上传走访材料成功:{add_attachments.json()}")

    def test_minutes(self):
        """
        贴妙记/文档 URL,拉内容写进visit
        """
        # post /api/v1/minutes/parse
        add_parse = requests.post(
            url=f"{BASE_URL}/api/v1/minutes/parse",
            json={
                "enterpriseId": self.enterprise_id[0],
                "visitId": self.visits_id[0],
                "rawContent": "https://fcn6bo5q7kmm.feishu.cn/docx/HNNTdbNocojItcxLzf8cwZ7Enfh"
            },
            headers=self.headers,
            verify=False
        )
        self.tasks_id.append(add_parse.json()['data']['taskId'])

        for i in range(120):
            r = requests.get(
                f"{BASE_URL}/api/v1/minutes/parsed/{self.tasks_id[0]}",
                headers=self.headers, verify=False
            ).json()
            status = r.get("data", {}).get("status", "")
            print(f"轮询 parseMinutes 第 {i + 1} 次: status={status}")
            if status == "completed":
                break
            elif status in ("failed", "canceled"):
                pytest.fail(f"parseMinutes 失败: {r}")
            time.sleep(5)
        else:
            pytest.fail("parseMinutes 10 分钟没完成")


    def test_analyze(self):
        """
        1.触发AI分析
        """
        # POST /api/v1/visits/{visitId}/analyze
        add_analyze = requests.post(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/analyze",
            json={},
            headers=self.headers,
            verify=False
        )
        self.tasks_id.append(add_analyze.json()['data']['taskId'])
        print(f"\n触发AI分析成功:{add_analyze.json()}")

    def test_tasks(self):
        """
        1.轮询task状态等completed
        """
        # GET /api/v1/minutes/parsed/{taskId}
        for i in range(60):
            get_tasks = requests.get(
                url=f"{BASE_URL}/api/v1/minutes/parsed/{self.tasks_id[1]}",
                headers=self.headers,
                verify=False
            )
            ai_summary = get_tasks.json()["data"]["visitRecord"]["aiSummary"]
            if ai_summary == "" and get_tasks.status_code == 200:
                print(f"\n轮询 {i + 1}次 获取任务结果中...")
                time.sleep(20)
            elif ai_summary != "" and get_tasks.status_code == 200:
                print(f"\n轮询 {i + 1}次 获取任务结果成功:{get_tasks.json()}")
                break
        else:
            pytest.fail("AI 分析任务 20 分钟未完成")

    def test_profile_updates(self):
        """
        1.看AI提取的画像更新
        """
        # GET /api/v1/visits/{enterpriseId}/profile-updates
        add_profile_updates = requests.get(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/profile-updates",
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert add_profile_updates.status_code == 200
        assert add_profile_updates.json()['data']['visitId'] == self.visits_id[0]
        # 响应结果
        print(f"\n获取profile_updates成功 id:{add_profile_updates.json()}")

    @pytest.mark.提交走访
    def test_submit(self):
        """
        1.把画像更新落库到企业
        """
        # POST /api/v1/visits/{visitId}/submit
        add_submit = requests.post(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}/submit",
            json={},
            headers=self.headers,
            verify=False
        )
        assert add_submit.status_code == 200
        assert add_submit.json()['data']['visitId'] == self.visits_id[0]
        print(f"\n提交走访成功:{add_submit.json()}")

    @pytest.mark.需求处理与任务分配
    def test_commit_visits(self):
        """
        1.提交
        """
        # put /api/v1/visits/01KV78D17ZCVHBC1KNEPSYH2HC
        commit_visits = requests.put(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
            json={"status": "submitted"},
            headers=self.headers,
            verify=False
        )
        # 断言状态码和响应结果
        assert commit_visits.status_code == 200
        assert commit_visits.json()['data']['status'] == "submitted"
        # 响应结果
        print(f"\n提交put:{commit_visits.json()}")

    def test_del_visits(self):
        """
        1.删除走访
        """
        # DELETE /api/v1/visits/{visitId}
        del_response = requests.delete(
            url=f"{BASE_URL}/api/v1/visits/{self.visits_id[0]}",
            headers=self.headers,
            verify=False
        )
        print(f"\n删除走访:{del_response.json()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
