import pytest
import requests
import urllib3

urllib3.disable_warnings()
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_client import base_url
from config.get_token import token
from utils.logger import get_logger
from utils.get_visits_data import get_csv_visits_data

"""
测试case:
01, 新增 待走访问题
02, 修改 待走访问题
03, 更新 答案
04, 
05, 
06, 
07, 
"""
# 企业画像-待走访问题
class TestVisitsProblem:
    logger = get_logger()
    visit_id = []
    del_visit_id = []
    update_visits_problem_comment_content = []
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.新增走访
    def test_new_visits(self):
        """
        测试用例：
        1. 新增企业走访成功
        """
        # POST/api/v1/visits新增企业走访
        url = f"{base_url}/api/v1/visits"
        body = {
            "enterpriseId": "7e367d34-ab10-41a6-b682-fc696bc76c63",
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

        # 打印实际值
        self.logger.info(f"✅新增走访成功: {new_visits_response.json()}\n")

    @pytest.mark.新增待走访问题
    @pytest.mark.parametrize("contents,sourceDepartments,sourcePersons", get_csv_visits_data())
    def test_visits_problem(self, contents, sourceDepartments, sourcePersons):
        """
        01.新增 多个待走访问题
        02.新增 纯数字
        03.新增 数字组合
        04.新增 纯字母
        05.新增 字母组合
        06.新增 特殊字符
        07.新增 特殊字符组合
        08.新增 所有字符组合
        09.新增 纯空格
        10.新增 空格组合
        11.新增 40个字符（最长40）
        12.新增 41个字符
        13.新增 为空
        """
        visits_problem_url = f"{base_url}/api/v1/enterprises/7e367d34-ab10-41a6-b682-fc696bc76c63/pending-questions"
        body = {
            "content": contents,
            "sourceDepartment": sourceDepartments,
            "sourcePerson": sourcePersons
        }
        visits_problem_response = requests.post(url=visits_problem_url, json=body, headers=self.headers, verify=False)

        # 断言状态码和响应结果
        assert visits_problem_response.status_code == 200
        assert visits_problem_response.json()["data"] is not None
        self.del_visit_id.append(visits_problem_response.json()['data']["item"]['id'])
        self.logger.info(f"✅新增待走访问题成功: 第{len(self.del_visit_id)}次, {visits_problem_response.json()}")

    @pytest.mark.修改待走访问题
    def test_update_visits_problem(self):
        """
        1.修改 单个/多个待走访问题
        2.修改 纯数字
        3.修改 数字组合
        4.修改 纯字母
        5.修改 字母组合
        6.修改 特殊字符
        7.修改 特殊字符组合
        8.修改 所有字符组合
        9.修改 纯空格
        10.修改 空格组合
        11.修改 40个字符（最长40）
        12.修改 41个字符
        13.修改 为空
        """
        # 定义要更新的数据列表
        update_data_list = get_csv_visits_data()

        # 没有数据跳过
        if not update_data_list:
            pytest.skip("没有测试数据")

        # 判断长度，用最小的len，避免索引错误
        min_len = min(len(self.del_visit_id), len(update_data_list))

        # for循环 遍历del_visit_id
        for i in range(min_len):
            update_visit = self.del_visit_id[i]
            update_contents, update_sourceDepartments, update_sourcePersons = update_data_list[i]

            update_visits_problem_url = f"{base_url}/api/v1/pending-questions/{update_visit}"
            body = {
                "content": update_contents,
                "sourceDepartment": update_sourceDepartments,
                "sourcePerson": update_sourcePersons
            }
            update_response = requests.put(url=update_visits_problem_url, json=body, headers=self.headers, verify=False)

            assert update_response.status_code == 200

        self.update_visits_problem_comment_content.append(update_response.json()["data"]["item"]["content"])
        self.logger.info(f"✅修改待走访问题成功: 第{i + 1}次 ID: {update_visit}, 响应:{update_response.json()}\n")

    @pytest.mark.更新答案
    def test_update_pending_question_answer(self):
        """
        1，新增所有评论
        """

        for i in range(len(self.update_visits_problem_comment_content)):
            update_content = self.update_visits_problem_comment_content[i]
            update_url = f"{base_url}/api/v1/pending-questions/{self.del_visit_id[i]}"
            payload = {
                "content": update_content,
                "answer": "接口测试答案",
                "updatedBy": ""
            }
            update_resp = requests.put(url=update_url, headers=self.headers, json=payload, verify=False)

            assert update_resp.status_code == 200

        self.logger.debug(f"content: {self.update_visits_problem_comment_content}")
        self.logger.info(f"✅更新成功, 最后一次返回值: {update_resp.json()}\n")

    @pytest.mark.删除待走访问题
    def test_del_visits_problem(self):
        """
        1.删除 多个待走访问题
        2.删除 纯数字
        3.删除 数字组合Å
        4.删除 纯字母
        5.删除 字母组合
        6.删除 特殊字符
        7.删除 特殊字符组合
        8.删除 所有字符组合
        9.删除 纯空格
        10.删除 空格组合
        11.删除 40个字符（最长40）
        12.删除 41个字符
        13.删除 为空
        """
        count_list = []
        for del_visit_id in self.del_visit_id:
            del_url = f"{base_url}/api/v1/pending-questions/{del_visit_id}"
            del_response = requests.delete(url=del_url, headers=self.headers, verify=False)

            count_list.append(del_response.json()["code"])
            # 断言状态码
            assert del_response.status_code == 200

        # 打印实际值
        self.logger.info(f"✅删除 {len(count_list)} 次待走访问题成功, {del_response.json()}\n")

    @pytest.mark.删除走访
    def test_del_visits(self):
        """
        1.删除走访卡片
        """
        # DELETE / api / v1 / visits / {visitId}
        for visit_id in self.visit_id:
            del_url = f"{base_url}/api/v1/visits/{visit_id}"
            del_response = requests.delete(url=del_url, headers=self.headers, verify=False)
            if del_response.json()["code"] == 0:
                assert del_response.status_code == 200
                self.logger.info("✅删除走访成功")
            elif del_response.json()["code"] != 0:
                assert del_response.json()["error"] == "走访记录不存在"
                self.logger.warning(f"⚠️ 删除走访失败,走访记录不存在: {del_response.json()}")
            else:
                self.logger.error(f"❌ 未知错误: {del_response.json()}\n")

    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
