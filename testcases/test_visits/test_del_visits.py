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
01, 删除走访 -- "准备阶段"
02, 删除走访 -- "沟通清单"
03, 删除走访 -- "走访阶段"
04, 删除走访 -- "结束阶段"
05, 删除走访 -- "跟进阶段"
06, 删除走访 -- "隐藏走访"

待补充...
07, 
08, 
"""


class TestDelVisits:
    logger = get_logger()
    r = random.randint(0, 99)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.删除准备阶段
    def test_del_ready_stage(self):
        """
        测试步骤:
        1, 新增 走访
        2, 删除 走访 -- "准备阶段"
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data']['enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")
            
            # ==================== [03] 删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[03]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[03]🙅删除失败, 返回:{del_visits.json()}"

            # 打印闭环结果
            self.logger.info(f"[03]✅准备阶段-删除走访成功, 返回:{del_visits.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
    
    @pytest.mark.删除沟通清单
    def test_del_order_stage(self):
        """
        测试步骤:
        1, 新增 走访
        2, 删除 走访 -- "准备阶段"
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data']['enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")
            
            # ==================== [03]扭转状态 checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert checklists.status_code == 200, f"[03]新增走访失败, 状态码:{checklists.status_code}, 返回:{checklists.json()}"

            # 断言返回结果
            assert checklists.json()['data'][
                       'status'] == "checklist", f"[03]扭转状态checklist失败, 返回:{checklists.json()}"
            assert checklists.json()['data'][
                       'enterpriseId'] == enterprise, f"[03]🙅企业id不一致, 返回enterpriseId:{checklists.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[03]✅扭转状态为:{checklists.json()['data']['status']}, 返回:{checklists.json()}")
            
            # ==================== [04] 删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[04]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[04]🙅删除失败, 返回:{del_visits.json()}"

            # 打印闭环结果
            self.logger.info(f"[04]✅沟通清单状态-删除走访成功, 返回:{del_visits.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.删除走访阶段
    def test_del_visits_stage(self):
        """
        测试步骤:
        1, 新增 走访
        2, 扭转 走访状态 -- "status" = "checklist"
        3, 扭转 走访状态 -- "status" = "visiting"
        4, 删除 走访 -- "走访阶段"
        """

        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")

            # ==================== [03]扭转状态 checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert checklists.status_code == 200, f"[03]新增走访失败, 状态码:{checklists.status_code}, 返回:{checklists.json()}"

            # 断言返回结果
            assert checklists.json()['data']['status'] == "checklist", f"[03]扭转状态checklist失败, 返回:{checklists.json()}"
            assert checklists.json()['data']['enterpriseId'] == enterprise, f"[03]🙅企业id不一致, 返回enterpriseId:{checklists.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[03]✅扭转状态为:{checklists.json()['data']['status']}, 返回:{checklists.json()}")

            # ==================== [04]扭转状态 visiting ====================
            visiting = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert visiting.status_code == 200, f"[04]新增走访失败, 状态码:{visiting.status_code}, 返回:{visiting.json()}"

            # 断言返回结果
            assert visiting.json()['data']['status'] == "visiting", f"[04]扭转状态checklist失败, 返回:{visiting.json()}"
            assert visiting.json()['data']['enterpriseId'] == enterprise, f"[04]企业id不一致, 返回enterpriseId:{visiting.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[04]✅扭转状态为:{visiting.json()['data']['status']}, 返回:{visiting.json()}")

            # ==================== [05]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[05]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[05]🙅删除失败, 返回:{del_visits.json()}"

            # 打印删除结果
            self.logger.info(f"[05]✅走访阶段-删除走访成功, 返回:{del_visits.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.删除结束阶段
    def test_del_over_stage(self):
        """
        测试步骤:
        1, 新增 走访
        2, 扭转 走访状态 -- "status"=="checklist"
        3, 扭转 走访状态 -- "status"=="visiting"
        3, 扭转 结束状态 -- "status"==""confirmed"
        4, 删除 走访 -- "结束阶段"
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")

            # ==================== [03]扭转状态 checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert checklists.status_code == 200, f"[03]新增走访失败, 状态码:{checklists.status_code}, 返回:{checklists.json()}"

            # 断言返回结果
            assert checklists.json()['data'][
                       'status'] == "checklist", f"[03]扭转状态checklist失败, 返回:{checklists.json()}"
            assert checklists.json()['data'][
                       'enterpriseId'] == enterprise, f"[03]🙅企业id不一致, 返回enterpriseId:{checklists.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[03]✅扭转状态为:{checklists.json()['data']['status']}, 返回:{checklists.json()}")

            # ==================== [04]扭转状态 visiting ====================
            visiting = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert visiting.status_code == 200, f"[04]新增走访失败, 状态码:{visiting.status_code}, 返回:{visiting.json()}"

            # 断言返回结果
            assert visiting.json()['data']['status'] == "visiting", f"[04]扭转状态checklist失败, 返回:{visiting.json()}"
            assert visiting.json()['data'][
                       'enterpriseId'] == enterprise, f"[04]企业id不一致, 返回enterpriseId:{visiting.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[04]✅扭转状态为:{visiting.json()['data']['status']}, ")

            # ==================== [05]扭转状态 confirmed ====================
            confirmed = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "confirmed"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert confirmed.status_code == 200, f"[05]新增走访失败, 状态码:{confirmed.status_code}, 返回:{confirmed.json()}"

            # 断言返回结果
            assert confirmed.json()['data']['status'] == "confirmed", f"[05]扭转状态checklist失败, 返回:{confirmed.json()}"
            assert confirmed.json()['data'][
                       'enterpriseId'] == enterprise, f"[05]企业id不一致, 返回enterpriseId:{confirmed.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[05]✅扭转状态为:{visiting.json()['data']['status']}, ")

            # ==================== [06]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[06]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[06]🙅删除失败, 返回:{del_visits.json()}"

            # 打印删除结果
            self.logger.info(f"[06]✅结束阶段-删除走访成功, 返回:{del_visits.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.删除跟进阶段
    def test_del_over_stage(self):
        """
        测试步骤:
        1, 新增 走访
        2, 扭转 走访状态 -- "status"=="checklist"
        3, 扭转 走访状态 -- "status"=="visiting"
        3, 扭转 结束状态 -- "status"=="confirmed"
        4, 扭转 跟进状态 -- "status"=="submitted"
        4, 删除 走访 -- "跟进阶段"
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")

            # ==================== [03]扭转状态 checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert checklists.status_code == 200, f"[03]新增走访失败, 状态码:{checklists.status_code}, 返回:{checklists.json()}"

            # 断言返回结果
            assert checklists.json()['data'][
                       'status'] == "checklist", f"[03]扭转状态checklist失败, 返回:{checklists.json()}"
            assert checklists.json()['data'][
                       'enterpriseId'] == enterprise, f"[03]🙅企业id不一致, 返回enterpriseId:{checklists.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[03]✅扭转状态为:{checklists.json()['data']['status']}, 返回:{checklists.json()}")

            # ==================== [04]扭转状态 visiting ====================
            visiting = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert visiting.status_code == 200, f"[04]新增走访失败, 状态码:{visiting.status_code}, 返回:{visiting.json()}"

            # 断言返回结果
            assert visiting.json()['data']['status'] == "visiting", f"[04]扭转状态checklist失败, 返回:{visiting.json()}"
            assert visiting.json()['data'][
                       'enterpriseId'] == enterprise, f"[04]企业id不一致, 返回enterpriseId:{visiting.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[04]✅扭转状态为:{visiting.json()['data']['status']}, 返回:{visiting.json()}")

            # ==================== [05]扭转状态 confirmed ====================
            confirmed = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "confirmed"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert confirmed.status_code == 200, f"[05]新增走访失败, 状态码:{confirmed.status_code}, 返回:{confirmed.json()}"

            # 断言返回结果
            assert confirmed.json()['data']['status'] == "confirmed", f"[05]扭转状态checklist失败, 返回:{confirmed.json()}"
            assert confirmed.json()['data'][
                       'enterpriseId'] == enterprise, f"[05]企业id不一致, 返回enterpriseId:{confirmed.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[05]✅扭转状态为:{confirmed.json()['data']['status']}, 返回:{confirmed.json()}")

            # ==================== [06]扭转状态 submitted ====================
            submitted = requests.put(
                url=f"{base_url}/api/v1/visits/{visits}",
                json={
                    "status": "submitted"
                },
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert submitted.status_code == 200, f"[06]新增走访失败, 状态码:{submitted.status_code}, 返回:{submitted.json()}"

            # 断言返回结果
            assert submitted.json()['data']['status'] == "submitted", f"[06]扭转状态checklist失败, 返回:{submitted.json()}"
            assert submitted.json()['data'][
                       'enterpriseId'] == enterprise, f"[06]企业id不一致, 返回enterpriseId:{submitted.json()['data']['enterpriseId']}, 列表enterpriseId{enterprise}"

            # 打印扭转结果
            self.logger.info(f"[06]✅扭转状态为:{submitted.json()['data']['status']}, 返回:{submitted.json()}")

        # ==================== [07]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[07]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[07]🙅删除失败, 返回:{del_visits.json()}"

            # 打印删除结果
            self.logger.info(f"[07]✅跟进阶段-删除走访成功, 返回:{del_visits.json()}\n")

        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    @pytest.mark.删除隐藏走访
    def test_del_hidden_visits(self):
        """
        测试步骤:
        1, 新增 走访
        2, 隐藏 走访
        3, 删除 隐藏走访
        """
        try:
            # ==================== [01] 获取随机企业 ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码和code为0
            assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 返回:{get_enterprises.json()}"
            assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"

            # append 企业id到enterprise列表
            enterprise = get_enterprises.json()['data']['list'][self.r]['id']

            # 结果打印日志
            self.logger.info(f"[01]✅获取随机企业id, 返回:{get_enterprises.json()['data']['list'][self.r]['id']}")

            # ==================== [02] 新增走访 ====================
            # POST/api/v1/visits新增企业走访
            new_visits_response = requests.post(
                url=f"{base_url}/api/v1/visits",
                json={
                    "enterpriseId": enterprise,  # str:企业id
                    "visitors": ["金阳"],  # list[str]:走访人
                    "participants": [{"name": "金阳"}],  # list[dict]:参会人
                    "source": "手动录入"  # str:来源
                },
                headers=self.headers,
                verify=False
            )

            # 断言状态码
            assert new_visits_response.status_code == 200, f"[02]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"

            # 断言返回结果
            assert new_visits_response.json()['code'] == 0, f"[02]新增走访失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data'][
                       'source'] == "手动录入", f"[02]手动录入失败:{new_visits_response.json()}"
            assert new_visits_response.json()['data']['enterpriseId'] == enterprise, f"[02]企业id不一致, list元素为:{enterprise}, 返回:{new_visits_response.json()['data']['enterprise']}"

            # 赋值 visits 为走访 id
            visits = new_visits_response.json()['data']['id']

            # 打印走访结果
            # self.logger.info(f"[02]列表:{enterprise}")
            self.logger.info(f"[02]✅新增走访成功, 返回:{new_visits_response.json()}")

            # ==================== [03]隐藏走访 ====================
            hide = requests.post(
                url=f"{base_url}/api/v1/visits/{visits}/hide",
                json={"hidden": True},
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert hide.status_code == 200, f"[03]新增走访失败, 状态码:{new_visits_response.status_code}, 返回:{new_visits_response.json()}"
            
            # 断言返回结果
            assert hide.json()['data']['hidden'] == True, f"[03]返回值不是True, 返回:{hide.json()}"
            
            # 打印隐藏结果
            self.logger.info(f"[03]✅隐藏走访成功, 返回:{hide.json()}")

            # ==================== [04]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits}",
                headers=self.headers,
                timeout=(30, 60),
                verify=False
            )
            # 断言状态码
            assert del_visits.status_code == 200, f"[04]新增走访失败, 状态码:{del_visits.status_code}, 返回:{del_visits.json()}"

            # 断言返回结果
            assert del_visits.json()['code'] == 0, f"[04]删除失败, 返回:{del_visits.json()}"

            # 打印删除结果
            self.logger.info(f"[04]✅跟进阶段-删除走访成功, 返回:{del_visits.json()}\n")


        except Exception as e:
            self.logger.error(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")

    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
