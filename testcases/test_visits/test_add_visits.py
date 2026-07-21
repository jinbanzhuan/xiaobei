import traceback
import random
import pytest
import requests
import urllib3

urllib3.disable_warnings()
from config.api_client import base_url
from config.get_token import token
from utils.logger import get_logger


"""
测试case:
01, 新增 走访
02, 新增 number个走访
03, 新增 错误走访
04, 新增 隐藏走访 -- "hidden"="Trues"
05, 新增 隐藏number个走访 -- "hidden"="Trues"
06, 显示 隐藏的走访 -- "hidden"="False"
07, 显示 number个隐藏的走访 -- "hidden"="False"
08, 
"""


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
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # 赋值 enterprise 为企业 id
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise is not None and len(
                enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码: {new_visits_response.status_code}, 响应: {new_visits_response.json()}"

            # 断言响应结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为: {enterprise}, 响应: {new_visits_response.json()['data']['enterpriseId']}"

            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterpriseId}")
            self.logger.info(f"[02]✅新增走访成功:{new_visits_response.json()}\n")

        except Exception as e:
            self.logger.error(f"报错信息: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.新增number个走访
    def test_add_multiple_visits(self):
        """
        测试步骤:
        1, input 走访数量(number最高99)
        2, 新增 number 个走访 case
        """
        try:
            number = random.randint(0, 99)
            enterprise = []
            visits = []
            # ==================== [01]获取随机企业id 存入enterprise ====================
            for i in range(number):
                r = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise列表
                enterprise.append(get_enterprises.json()['data']['list'][r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise is not None and len(
                    enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {i + 1} 次随机企业id成功: {enterprise}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise[i],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败, 状态码:{add_visits.status_code}, 响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise[
                    i], f"[02]企业id不一致, list元素为:{enterprise[i]}, 响应:{add_visits.json()['data']['enterpriseId']}"

                # append 走访id到visits列表
                visits.append(add_visits.json()['data']['id'])
            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visitsId}")
            # self.logger.info(f"[02]企业列表: {enterpriseId}")
            self.logger.info(f"[02]✅新增 {i + 1} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03]闭环 ====================
            for visitsId in visits:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visitsId}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert del_visits.status_code == 200, f"[03]新增走访失败, 状态码:{del_visits.status_code}, 响应:{del_visits.json()}"

                # 断言响应结果
                assert del_visits.json()['code'] == 0, f"[03]🙅删除失败, 响应:{del_visits.json()}"

            # 打印闭环结果
            self.logger.info(f"[03]✅删除 {len(visits)} 次成功, 最后一次删除返回值:{del_visits.json()}")

        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.新增错误走访
    def test_add_visits_fail(self):
        """
        测试步骤:
        1, 新增走访失败 case
        """
        try:
            # 故意使用明显无效的企业 id, 让后端返回失败, 验证错误处理路径
            enterprise = "invalid-enterprise-id-for-fail-case"

            # ==================== [01] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            add_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )

            # 断言状态码
            assert add_visits_response.status_code == 200, f"[01]查询企业id失败, 状态码: {add_visits_response.status_code}, 响应: {add_visits_response.json()}"

            # 断言响应结果
            assert add_visits_response.json()['code'] == -1, f"[01]新增走访失败:{add_visits_response.json()}"
            assert add_visits_response.json()[
                       'error'] == f"企业不存在或已删除: {enterprise}", f"[01]手动录入失败:{add_visits_response.json()}"

            # 打印走访结果
            # self.logger.info(f"[01]列表: {enterprise}")
            self.logger.info(f"[01]✅新增走访失败:{add_visits_response.json()}\n")

        except Exception as e:
            self.logger.info(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.新增隐藏走访
    def test_hidden_trues(self):
        """
        测试步骤:
        1, 新增走访
        2, 隐藏走访 case
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # 赋值 enterprise 为企业 id
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise is not None and len(enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert add_visits.status_code == 200, f"[02]新增走访失败, 状态码: {add_visits.status_code}, 响应: {add_visits.json()}"

            # 断言响应结果
            assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
            assert add_visits.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
            assert add_visits.json()['data'][
                       'enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为: {enterprise}, 响应: {add_visits.json()['data']['enterpriseId']}"

            # append 走访id到visitsId列表
            visits = add_visits.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterprise}")
            self.logger.info(f"[02]✅新增走访成功:{add_visits.json()}")

            # ==================== [03] 隐藏走访 ====================
            hide_true = requests.post(
                url=f"{base_url}/api/v1/visits/{visits}/hide",
                json={"hidden": True},
                headers=self.headers,
                verify=False
            )
            # 断言状态码
            assert hide_true.status_code == 200, f"[03]隐藏走访失败, 状态码: {hide_true.status_code}, 响应: {hide_true.json()}"

            # 断言响应结果
            assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
            assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[03]✅隐藏走访成功:{hide_true.json()}\n")

        except Exception as e:
            self.logger.error(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.新增隐藏number个走访
    def test_hidden_multiple_trues(self):
        """
        测试步骤:
        1, 新增多个走访
        2, 隐藏多个走访 case
        """
        try:
            number = random.randint(0, 99)
            enterprise = []
            visits = []
            # ==================== [01]获取随机企业id 存入enterprise ====================
            for i in range(number):
                random_number = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise列表
                enterprise.append(get_enterprises.json()['data']['list'][self.r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise is not None and len(
                    enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {number} 次随机企业id成功: {enterprise}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise[i],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败, 状态码:{add_visits.status_code}, 响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise[
                    i], f"[02]企业id不一致, list元素为:{enterprise[i]}, 响应:{add_visits.json()['data']['enterpriseId']}"

                # append 走访id到visits列表
                visits.append(add_visits.json()['data']['id'])
            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visits}")
            # self.logger.info(f"[02]企业列表: {enterpriseId}")
            self.logger.info(f"[02]✅新增 {number} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03] 隐藏多个走访 ====================
            for visitsId in visits:
                hide_true = requests.post(
                    url=f"{base_url}/api/v1/visits/{visitsId}/hide",
                    json={"hidden": True},
                    headers=self.headers,
                    verify=False
                )
                # 断言状态码
                assert hide_true.status_code == 200, f"[03]隐藏走访失败, 状态码: {hide_true.status_code}, 响应: {hide_true.json()}"

                # 断言响应结果
                assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
                assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[03]✅隐藏 {len(visits)} 次走访成功:{hide_true.json()}\n")

            # ==================== [04]闭环 ====================
            for visitsId in visits:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visitsId}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert del_visits.status_code == 200, f"[04]新增走访失败, 状态码:{del_visits.status_code}, 响应:{del_visits.json()}"

                # 断言响应结果
                assert del_visits.json()['code'] == 0, f"[04]🙅删除失败, 响应:{del_visits.json()}"

            # 打印闭环结果
            self.logger.info(f"[04]✅删除 {len(visits)} 次成功, 最后一次删除返回值:{del_visits.json()}")

        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.显示隐藏的走访
    def test_hidden_false(self):
        """
        测试步骤:
        1, 新增走访
        2, 隐藏走访 case
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # 赋值 enterprise 为企业 id
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 断言是否添加成功, 列表元素是否为空
            assert enterprise is not None and len(
                enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [z] 新增走访 ====================
            add_visits = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str: 企业id
                    "visitors": ["金阳"],  # list[str]: 走访人
                    "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                    "source": "手动录入"  # str: 来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert add_visits.status_code == 200, f"[02]新增走访失败, 状态码: {add_visits.status_code}, 响应: {add_visits.json()}"

            # 断言响应结果
            assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
            assert add_visits.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为: {enterprise}, 响应: {add_visits.json()['data']['enterpriseId']}"

            # append 走访id到visitsId列表
            visits = add_visits.json()['data']['id']
            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterpriseId}")
            self.logger.info(f"[02]✅新增走访成功:{add_visits.json()}")

            # ==================== [03] 隐藏走访 ====================
            hide_true = requests.post(
                url=f"{base_url}/api/v1/visits/{visits}/hide",
                json={"hidden": True},
                headers=self.headers,
                verify=False
            )
            # 断言状态码
            assert hide_true.status_code == 200, f"[03]隐藏走访失败, 状态码: {hide_true.status_code}, 响应: {hide_true.json()}"

            # 断言响应结果
            assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
            assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            # 打印走访结果
            self.logger.info(f"[03]✅隐藏走访成功:{hide_true.json()}")

            # ==================== [04] 显示走访 ====================
            hide_false = requests.post(
                url=f"{base_url}/api/v1/visits/{visits}/hide",
                json={"hidden": False},
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert hide_false.status_code == 200, f"[04]显示走访失败, 状态码: {hide_false.status_code}, 响应: {hide_false.json()}"

            # 断言响应结果
            assert hide_false.json()['code'] == 0, f"[04]显示走访失败:{hide_false.json()}"
            assert hide_false.json()['data']['hidden'] == False, f"[04]显示走访hidden状态错误:{hide_false.json()}"

            # 打印走访结果
            self.logger.info(f"[04]✅显示走访成功:{hide_false.json()}\n")

        except Exception as e:
            self.logger.error(f"报错信息: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.新增显示number个走访
    def test_hidden_multiple_false(self):
        """
            测试步骤:
            1, 新增多个走访
            2, 隐藏多个走访
            3, 显示多个走访 case
        """
        try:
            number = random.randint(1, 99)
            enterprise = []
            visits = []
            # ==================== [01]获取随机企业id 存入enterprise ====================
            for i in range(number):
                random_number = random.randint(0, 10)
                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )

                # 断言状态码和code为0
                assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
                assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

                # append 企业id到enterprise列表
                enterprise.append(get_enterprises.json()['data']['list'][self.r]['id'])

                # 断言是否添加成功, 列表元素是否为空
                assert enterprise is not None and len(
                    enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"

            # 结果打印日志
            self.logger.info(f"[01]✅获取 {i+1} 次随机企业id成功: {enterprise}")

            # ==================== [02]新增走访 N 次 ====================
            for i in range(len(enterprise)):
                add_visits = requests.post(
                    url=f"{base_url}/api/v1/visits",
                    json={
                        "enterpriseId": enterprise[i],  # str: 企业id
                        "visitors": ["金阳"],  # list[str]: 走访人
                        "participants": [{"name": "金阳"}],  # list[dict]: 参会人
                        "source": "手动录入"  # str: 来源
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                # 断言状态码
                assert add_visits.status_code == 200, f"新增走访失败, 状态码:{add_visits.status_code}, 响应:{add_visits.json()}"

                # 断言响应结果
                assert add_visits.json()['code'] == 0, f"[02]新增走访失败:{add_visits.json()}"
                assert add_visits.json()['data'][
                           'source'] == "手动录入", f"[02]手动录入失败:{add_visits.json()}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise[
                    i], f"[02]企业id不一致, list元素为:{enterprise[i]}, 响应:{add_visits.json()['data']['enterpriseId']}"

                # append 走访id到visitsId列表
                visits.append(add_visits.json()['data']['id'])
            # 打印走访结果
            # self.logger.info(f"[02]走访列表: {visits}")
            # self.logger.info(f"[02]企业列表: {enterprise}")
            self.logger.info(f"[02]✅新增 {number} 次成功, 最后一次走访返回值:{add_visits.json()}")

            # ==================== [03] 隐藏多个走访 ====================
            for visitsId in visits:
                hide_true = requests.post(
                    url=f"{base_url}/api/v1/visits/{visitsId}/hide",
                    json={"hidden": True},
                    headers=self.headers,
                    verify=False
                )
                # 断言状态码
                assert hide_true.status_code == 200, f"[03]隐藏走访失败, 状态码: {hide_true.status_code}, 响应: {hide_true.json()}"

                # 断言响应结果
                assert hide_true.json()['code'] == 0, f"[03]隐藏走访失败:{hide_true.json()}"
                assert hide_true.json()['data']['hidden'] == True, f"[03]隐藏走访hidden状态错误:{add_visits.json()}"

            self.logger.info(f"[03]✅隐藏 {len(visits)} 次走访成功:{hide_true.json()}")

            # ==================== [04] 显示走访 ====================
            for visitsId in visits:
                hide_false = requests.post(
                    url=f"{base_url}/api/v1/visits/{visitsId}/hide",
                    json={"hidden": False},
                    headers=self.headers,
                    verify=False
                )

                # 断言状态码
                assert hide_false.status_code == 200, f"[04]显示走访失败, 状态码: {hide_false.status_code}, 响应: {hide_false.json()}"

                # 断言响应结果
                assert hide_false.json()['code'] == 0, f"[04]显示走访失败:{hide_false.json()}"
                assert hide_false.json()['data']['hidden'] == False, f"[04]显示走访hidden状态错误:{hide_false.json()}"

            # 打印走访结果
            self.logger.info(f"[04]✅显示 {len(visits)} 次走访成功:{hide_false.json()}\n")

            # ==================== [05]闭环 ====================
            for visitsId in visits:
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visitsId}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                assert del_visits.status_code == 200, f"[05]删除走访失败, 响应码错误:{del_visits.status_code}"
                assert del_visits.json()['code'] == 0, f"[05]删除走访失败:{del_visits.json()}"


        except Exception as e:
            self.logger.info(f"报错信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.删除全部走访防报错
    def test_del_all(self):
        try:
            # ==================== [01] 全量扫描（含隐藏 & 所有阶段） ====================
            get_all = requests.get(
                url=f"{base_url}/api/v1/visits?page=1&pageSize=200",
                headers=self.headers,
                timeout=(10, 30),
                verify=False,
            )
            # 断言状态码
            assert get_all.status_code == 200, \
                f"[01]🙅 拉全量走访失败, 状态码 {get_all.status_code}, body={get_all.json()}"

            # 只保留后端权限判为可删的走访(permissions.canDelete == True)
            # 等价于"仅本人创建 / 有删除权限"，把过滤前置到查询阶段，避免无意义 DELETE
            data = get_all.json().get('data') or {}
            all_list = data.get('list') or []
            total = data.get('total')
            all_ids = [
                item['id']
                for item in all_list
                if isinstance(item, dict)
                   and item.get('id')
                   and (item.get('permissions') or {}).get('canDelete') is True
            ]

            # 打印结果
            self.logger.info(
                f"[01]✅全量 total={total}, 本次返回 {len(all_list)} 条, "
                f"可删(canDelete=True) {len(all_ids)} 条: {all_ids}"
            )

            # ==================== [02] 逐个删除 ====================
            for i, visits_id in enumerate(all_ids, 1):
                del_visits = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visits_id}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False,
                )
                assert del_visits.status_code == 200, \
                    f"[02]🙅删除 {visits_id} 失败, 状态码 {del_visits.status_code}"

                resp = del_visits.json()
                # 防御性 skip: canDelete 前置过滤后理论上不会命中, 保留兜底以防后端权限口径变化
                if resp.get('error') == "仅走访创建人可删除该走访":
                    self.logger.warning(f"非本人走访:{resp}")
                    continue
                assert resp.get('code') == 0, \
                    f"[02]🙅删除 {visits_id} 失败, 响应: {resp}"
                # self.logger.info(f"[02]🗑️已删除 {i}/{len(all_ids)}: {visits_id}")

            self.logger.info(f"[02]✅兜底删除完成, 共 {len(all_ids)} 条\n")

        except Exception as e:
            self.logger.error(f"测试异常: {e}")
            self.logger.error(f"堆栈信息: \n{traceback.format_exc()} \n")

    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
