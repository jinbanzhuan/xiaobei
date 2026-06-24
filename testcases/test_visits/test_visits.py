import pytest
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_client import base_url
from config.get_token import token
import urllib3

urllib3.disable_warnings()

class TestVisits:
    visit_id = []
    enterprise_id=[]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.新增走访
    @pytest.mark.parametrize("enterprise_id", [
        "7e367d34-ab10-41a6-b682-fc696bc76c63",
        "dc5d07e8-226e-4c82-89b4-a447cddbc00d"
    ])
    def test_new_visits(self, enterprise_id):
        """
        测试用例：
        1. 新增企业走访成功
        """
        # POST/api/v1/visits新增企业走访
        url = f"{base_url}/api/v1/visits"
        body = {
            "enterpriseId": enterprise_id,
            "visitors": [],
            "participants": [{"name": "金阳"}],
            "source": "手动录入"
        }
        new_visits_response = requests.post(url=url, json=body, headers=self.headers, verify=False)

        # 断言状态码和响应结果
        assert new_visits_response.status_code == 200
        assert new_visits_response.json()['data']['source'] == "手动录入"

        # 添加新增的走访id
        self.visit_id.append(new_visits_response.json()['data']['id'])

        # 响应结果
        print(f"\n新增走访成功:{new_visits_response.json()}")

    @pytest.mark.隐藏走访
    def test_hidden_trues(self):
        """
        1.显示的走访卡片隐藏成功
        """
        # POST/api/v1/visits/{visitId}/hide   显示企业走访卡片
        for visit_id in self.visit_id:
            hide_url = f"{base_url}/api/v1/visits/{visit_id}/hide"
            body = {"hidden": True}
            hide_response = requests.post(url=hide_url, json=body, headers=self.headers, verify=False)
            assert hide_response.status_code == 200
            assert hide_response.json()['data']['hidden'] == True
            print(f"\n隐藏走访成功:{hide_response.json()}")

    @pytest.mark.显示走访
    def test_hidden_falses(self):
        """
        1.隐藏的走访卡片显示成功
        """
        # POST/api/v1/visits/{visitId}/hide   隐藏企业走访卡片
        hide_url = f"{base_url}/api/v1/visits/{self.visit_id[1]}/hide"
        body = {"hidden": False}
        hide_responses = requests.post(url=hide_url, json=body, headers=self.headers, verify=False)
        assert hide_responses.status_code == 200
        assert hide_responses.json()['data']['hidden'] == False
        print(f"\n显示走访成功,返回值:{hide_responses.json()['data']['hidden']}")

    @pytest.mark.提交走访
    def test_submit_visits(self):
        """
        1.提交走访成功
        """
        # POST/api/v1/visits/{visitId}/submit
        for i in range(len(self.enterprise_id)):
            submit_url = f"{base_url}/api/v1/visits/{self.visit_id[1]}/submit"
            body = {
                "enterpriseId": self.enterprise_id[i],
                "meetingTime": "2026-06-10T15:00:00Z",
                "attendees": ["金阳"],
            },
            submit_response = requests.post(url=submit_url, json=body, headers=self.headers, verify=False)
            assert submit_response.status_code == 200
            print(f"\n提交走访成功:{submit_response.json()}")

    @pytest.mark.删除走访
    def test_del_visits(self):
        """
        1.删除显示的走访卡片
        2.删除隐藏的走访卡片
        """
        # DELETE/api/v1/visits/{visitId}
        for visit_id in self.visit_id:
            del_url = f"{base_url}/api/v1/visits/{visit_id}"
            del_response = requests.delete(url=del_url, headers=self.headers, verify=False)
            if del_response.json()["code"] == 0:
                assert del_response.status_code == 200
                print(f"\n删除走访成功:{del_response.json()}")
            elif del_response.json()["code"] != 0:
                assert del_response.json()["error"] == "走访记录不存在"
                print(f"\n删除走访失败,走访记录不存在:{del_response.json()}")
            else:
                print(f"\n未知错误:{del_response.json()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
