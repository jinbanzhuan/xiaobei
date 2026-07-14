import traceback
import random
import pytest
import requests
# import os
# import sys
#
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_client import base_url
from config.get_token import token
from config.logger import get_logger
import urllib3

urllib3.disable_warnings()


class TestAddVisits:
    logger = get_logger()
    r = random.randint(0, 99)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.新增走访
    def test_add_visits_success(self):
        """
        测试步骤:
        1, 新增走访成功 case
        """
        try:
            enterprise_id = []

            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise_id列表
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id[0],  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败,状态码: {new_visits_response.status_code},响应: {new_visits_response.json()}"

            # 断言响应结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]企业id不一致, list元素为: {enterprise_id},响应: {new_visits_response.json()['data']['enterprise_id']}"

            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增走访成功:{new_visits_response.json()}")

        except Exception as e:
            self.logger.error(f"报错信息: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.新增number个走访
    def test_add_multiple_visits(self):
        """
        测试步骤:
        1, input 走访数量(number最高99)
        2, 新增 number 个走访 case
        """
        try:
            number = random.randint(0, 99)
            enterprise_id = []
            visits_id = []
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            for i in range(number):
                random_number = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise_id列表
                enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise_id is not None and len(
                    enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {number} 次随机企业id成功: {enterprise_id}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise_id)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise_id[0],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败,状态码:{add_visits.status_code},响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                    i], f"[02]企业id不一致, list元素为:{enterprise_id[i]},响应:{add_visits.json()['data']['enterprise_id']}"

                # append 走访id到visits_id列表
                visits_id.append(add_visits.json()['data']['id'])

            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visits_id}")
            # self.logger.info(f"[02]企业列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增 {number} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03]闭环 ====================
            for visits in visits_id:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visits}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                assert del_visits.status_code == 200, f"[03]🙅删除走访失败,响应码错误:{del_visits.status_code}"
                assert del_visits.json()['code'] == 0, f"[03]🙅删除走访失败:{del_visits.json()}"

        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.新增走访失败
    def test_add_visits_fail(self):
        """
        测试步骤:
        1, 新增走访失败 case
        """
        try:
            enterprise_id = ["910c4f2d-5734-4d54-8cb9-8c3c64b66d13"]

            # ==================== [01] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            add_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id[0],  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )

            # 断言状态码
            assert add_visits_response.status_code == 200, f"[01]查询企业id失败,状态码: {add_visits_response.status_code},响应: {add_visits_response.json()}"

            # 断言响应结果
            assert add_visits_response.json()['code'] == -1, f"[01]新增走访失败:{add_visits_response.json()}"
            assert add_visits_response.json()[
                       'error'] == f"企业不存在或已删除: {enterprise_id[0]}", f"[01]手动录入失败:{add_visits_response.json()}"

            # 打印走访结果
            # self.logger.info(f"[01]列表: {enterprise_id}")
            self.logger.info(f"[01]✅新增走访失败:{add_visits_response.json()}")

        except Exception as e:
            self.logger.info(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.隐藏走访
    def test_hidden_trues(self):
        """
        测试步骤:
        1, 新增走访
        2, 隐藏走访 case
        """
        try:
            enterprise_id = []
            visits_id = []

            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise_id列表
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id[0],  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert add_visits.status_code == 200, f"[02]新增走访失败,状态码: {add_visits.status_code},响应: {add_visits.json()}"

            # 断言响应结果
            assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
            assert add_visits.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]企业id不一致, list元素为: {enterprise_id},响应: {add_visits.json()['data']['enterprise_id']}"

            # append 走访id到visits_id列表
            visits_id.append(add_visits.json()['data']['id'])

            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增走访成功:{add_visits.json()}")

            # ==================== [02] 隐藏走访 ====================
            hide_true = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/hide",
                json={"hidden": True},
                headers=self.headers, 
                verify=False
            )
            # 断言状态码
            assert hide_true.status_code == 200, f"[02]隐藏走访失败,状态码: {hide_true.status_code},响应: {hide_true.json()}"

            # 断言响应结果
            assert hide_true.json()['code'] == 0, f"[02]隐藏走访失败:{hide_true.json()}"
            assert hide_true.json()['data']['hidden'] == True, f"[02]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[02]✅隐藏走访成功:{hide_true.json()}")

        except Exception as e:
            self.logger.error(f"报错信息: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.隐藏number个走访
    def test_hidden_multiple_trues(self):
        """
        测试步骤:
        1, 新增多个走访
        2, 隐藏多个走访 case
        """
        try:
            number = random.randint(0, 99)
            enterprise_id = []
            visits_id = []
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            for i in range(number):
                random_number = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise_id列表
                enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise_id is not None and len(
                    enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {number} 次随机企业id成功: {enterprise_id}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise_id)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise_id[0],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败,状态码:{add_visits.status_code},响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                    i], f"[02]企业id不一致, list元素为:{enterprise_id[i]},响应:{add_visits.json()['data']['enterprise_id']}"

                # append 走访id到visits_id列表
                visits_id.append(add_visits.json()['data']['id'])

            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visits_id}")
            # self.logger.info(f"[02]企业列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增 {number} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03] 隐藏多个走访 ====================
            for visits in visits_id:
                hide_true = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits}/hide",
                    json={"hidden": True},
                    headers=self.headers,
                    verify=False
                )
                # 断言状态码
                assert hide_true.status_code == 200, f"[03]隐藏走访失败,状态码: {hide_true.status_code},响应: {hide_true.json()}"

                # 断言响应结果
                assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
                assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[03]✅隐藏 {len(visits_id)} 次走访成功:{hide_true.json()}")

            # ==================== [04]闭环 ====================
            for visits in visits_id:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visits}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                assert del_visits.status_code == 200, f"[04]删除走访失败,响应码错误:{del_visits.status_code}"
                assert del_visits.json()['code'] == 0, f"[04]删除走访失败:{del_visits.json()}"

        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.显示走访
    def test_hidden_false(self):
        """
                测试步骤:
                1, 新增走访
                2, 隐藏走访 case
                """
        try:
            enterprise_id = []
            visits_id = []

            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise_id列表
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise_id[0],  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert add_visits.status_code == 200, f"[02]新增走访失败,状态码: {add_visits.status_code},响应: {add_visits.json()}"

            # 断言响应结果
            assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
            assert add_visits.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]企业id不一致, list元素为: {enterprise_id},响应: {add_visits.json()['data']['enterprise_id']}"

            # append 走访id到visits_id列表
            visits_id.append(add_visits.json()['data']['id'])

            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增走访成功:{add_visits.json()}")

            # ==================== [02] 隐藏走访 ====================
            hide_true = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/hide",
                json={"hidden": True},
                headers=self.headers,
                verify=False
            )
            # 断言状态码
            assert hide_true.status_code == 200, f"[02]隐藏走访失败,状态码: {hide_true.status_code},响应: {hide_true.json()}"

            # 断言响应结果
            assert hide_true.json()['code'] == 0, f"[02]隐藏走访失败:{hide_true.json()}"
            assert hide_true.json()['data']['hidden'] == True, f"[02]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[02]✅隐藏走访成功:{hide_true.json()}")

            # ==================== [03] 显示走访 ====================
            hide_false = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/hide",
                json={"hidden": False},
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert hide_false.status_code == 200, f"[02]显示走访失败,状态码: {hide_false.status_code},响应: {hide_false.json()}"

            # 断言响应结果
            assert hide_false.json()['code'] == 0, f"[02]显示走访失败:{hide_false.json()}"
            assert hide_false.json()['data']['hidden'] == False, f"[02]显示走访hidden状态错误:{hide_false.json()}"

            # 打印走访结果
            self.logger.info(f"[02]✅显示走访成功:{hide_false.json()}")

        except Exception as e:
            self.logger.error(f"报错信息: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    @pytest.mark.显示number个走访
    def test_hidden_multiple_false(self):
        """
            测试步骤:
            1, 新增多个走访
            2, 隐藏多个走访
            3, 显示多个走访 case
            """
        try:
            number = random.randint(0, 99)
            enterprise_id = []
            visits_id = []
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            for i in range(number):
                random_number = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败,状态码:{get_enterprises.status_code},响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise_id列表
                enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise_id is not None and len(
                    enterprise_id) > 0, f"[01]新增企业id失败,列表为空:{enterprise_id}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {number} 次随机企业id成功: {enterprise_id}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise_id)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise_id[0],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败,状态码:{add_visits.status_code},响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                    i], f"[02]企业id不一致, list元素为:{enterprise_id[i]},响应:{add_visits.json()['data']['enterprise_id']}"

                # append 走访id到visits_id列表
                visits_id.append(add_visits.json()['data']['id'])

            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visits_id}")
            # self.logger.info(f"[02]企业列表: {enterprise_id}")
            self.logger.info(f"[02]✅新增 {number} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03] 隐藏多个走访 ====================
            for visits in visits_id:
                hide_true = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits}/hide",
                    json={"hidden": True},
                    headers=self.headers,
                    verify=False
                )
                # 断言状态码
                assert hide_true.status_code == 200, f"[03]隐藏走访失败,状态码: {hide_true.status_code},响应: {hide_true.json()}"

                # 断言响应结果
                assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
                assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            self.logger.info(f"[03]✅隐藏 {len(visits_id)} 次走访成功:{hide_true.json()}")

            # ==================== [04] 显示走访 ====================
            for visits in visits_id:
                hide_false = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits}/hide",
                    json={"hidden": False},
                    headers=self.headers,
                    verify=False
                )

                # 断言状态码
                assert hide_false.status_code == 200, f"[04]显示走访失败,状态码: {hide_false.status_code},响应: {hide_false.json()}"

                # 断言响应结果
                assert hide_false.json()['code'] == 0, f"[04]显示走访失败:{hide_false.json()}"
                assert hide_false.json()['data']['hidden'] == False, f"[04]显示走访hidden状态错误:{hide_false.json()}"

            # 打印走访结果
            self.logger.info(f"[04]✅显示 {len(visits_id)} 次走访成功:{hide_false.json()}")

            # ==================== [05]闭环 ====================
            for visits in visits_id:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visits}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                assert del_visits.status_code == 200, f"[05]删除走访失败,响应码错误:{del_visits.status_code}"
                assert del_visits.json()['code'] == 0, f"[05]删除走访失败:{del_visits.json()}"

        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")

    # @pytest.mark.提交走访
    # def test_submit_visits(self):
    #     """
    #     1.提交走访成功
    #     """
    #     # POST/api/v1/visits/{visitId}/submit
    #     for i in range(len(self.enterprise_id)):
    #         submit_url = f"{base_url}/api/v1/visits/{self.visit_id[1]}/submit"
    #         body = {
    #             "enterpriseId": self.enterprise_id[i],
    #             "meetingTime": "2026-06-10T15:00:00Z",
    #             "attendees": ["金阳"],
    #         },
    #         submit_response = requests.post(url=submit_url, json=body, headers=self.headers, verify=False)
    #         assert submit_response.status_code == 200
    #         self.logger.info(f"\n提交走访成功:{submit_response.json()}")



    @pytest.mark.删除走访兜底
    def test_del(self):
        try:
            while True:
                # ==================== [01]查询页面已经创建的企业 ====================
                get_page = requests.get(
                    url=f"{base_url}/api/v1/visit-workbench/preparation-tasks?page=1&pageSize=60",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False,
                )
                assert get_page.status_code == 200, f"\n🙅 获取分页失败,响应码错误: {get_page.status_code}"
                task_id_list = [item['id'] for item in get_page.json()['items']]
                self.logger.info(f"✅ 共获取 {len(task_id_list)} 个 id: {task_id_list}")

                # ==================== [02]删除已经查到的公司 ====================
                number = 0
                for visits_id in task_id_list:
                    number += 1
                    del_visits = requests.delete(
                        url=f"{base_url}/api/v1/visits/{visits_id}",
                        headers=self.headers,
                        timeout=(10, 30),
                        verify=False
                    )
                    assert del_visits.status_code == 200, f"[06]🙅删除走访失败,响应码错误:{del_visits.status_code}"
                    assert del_visits.json()['code'] == 0, f"[06]🙅删除走访失败:{del_visits.json()}"
                    self.logger.info(f"已经删除 {number} 条: {del_visits.json()}")
                if task_id_list is not None:
                    self.logger.info(f"删除兜底，已经没有公司了")
                    break


        except Exception as e:
            self.logger.error(f"测试异常: {e}")
            self.logger.error(f"堆栈信息: \n{traceback.format_exc()} \n")
            raise


    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
