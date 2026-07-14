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






class TestDelVisits:
    logger = get_logger()
    r = random.randint(0, 99)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.准备阶段_删除走访
    def test_del_ready_stage(self):
        """
        1, 准备阶段-删除走访
        """
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            """
            1,case
            """
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )

            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01] ✅ 获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                timeout=(10, 30),
                verify=False
            )
            assert add_visits.status_code == 200, f"[02]🙅新增走访失败,️响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]🙅新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            self.logger.info(f"[02] ✅ 新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert del_visits.status_code == 200, f"[03]🙅删除走访失败,️响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"[03]🙅删除走访失败:{del_visits.json()}"

        except AssertionError as e:
            self.logger.error(f" ☹️ 断言失败: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except IndexError as e:
            self.logger.info(f" ☹️ 索引错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except Exception as e:
            self.logger.info(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        else:
            self.logger.info(f"[03] ✅ 准备阶段-删除走访成功:{del_visits.json()}\n")

    @pytest.mark.走访阶段_删除走访
    def test_del_visits_stage(self):
        """
        1, 走访阶段-删除走访
        """
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )

            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业id失败,️响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01] ✅ 获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                timeout=(10, 30),
                verify=False
            )
            assert add_visits.status_code == 200, f"[02]🙅新增走访失败,响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]🙅新增走访失败,企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            visits_id.append(add_visits.json()['data']['id'])
            self.logger.info(f"[02] ✅ 新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]扭转状态checklist ====================
            checklists = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "checklist"
                },
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert checklists.status_code == 200, f"[03]🙅扭转状态checklist失败,响应码错误:{checklists.status_code}"
            assert checklists.json()['data'][
                       'status'] == "checklist", f"[03]🙅扭转状态checklist失败:{checklists.json()}"
            assert checklists.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[03]🙅企业id不一致,返回值enterpriseId:{checklists.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            self.logger.info(f"[03] ✅ 扭转状态为:{checklists.json()['data']['status']}")

            # ==================== [04]扭转状态visitings ====================
            visitings = requests.put(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                json={
                    "status": "visiting"
                },
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert visitings.status_code == 200, f"[04]🙅扭转状态visitings失败,响应码错误:{visitings.status_code}"
            assert visitings.json()['data']['status'] == "visiting", f"[04]🙅扭转状态checklist失败:{visitings.json()}"
            assert visitings.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[04]🙅企业id不一致,返回值enterpriseId:{visitings.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id}"
            self.logger.info(f"[04] ✅ 扭转状态为:{visitings.json()['data']['status']},跳转到 走访阶段")

            # ==================== [05]删除走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert del_visits.status_code == 200, f"[05]🙅删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"[05]🙅删除走访失败:{del_visits.json()}"

        except AssertionError as e:
            self.logger.error(f" ☹️ 断言失败: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except IndexError as e:
            self.logger.info(f" ☹️ 索引错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except Exception as e:
            self.logger.info(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        else:
            self.logger.info(f"[05] ✅ 走访阶段-删除走访成功:{del_visits.json()}\n")

    @pytest.mark.删除隐藏走访
    def test_del_hidden_visits(self):
        """
        1, 删除隐藏走访
        """
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业失败,响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][self.r]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01] ✅ 获取随机企业id:{get_enterprises.json()['data']['list'][self.r]['id']}")

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
                timeout=(10, 30),
                verify=False
            )
            assert add_visits.status_code == 200, f"[02]🙅新增走访失败,响应码错误:{add_visits.status_code}"
            assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                0], f"[02]🙅企业id不一致,返回值enterpriseId:{add_visits.json()['data']['enterpriseId']},列表enterpriseId{enterprise_id[0]}"
            visits_id.append(add_visits.json()['data']['id'])
            self.logger.info(f"[02] ✅ 新增走访:{add_visits.json()['data']['createdAt']}")

            # ==================== [03]隐藏走访 ====================
            hide = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/hide",
                json={"hidden": True},
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert hide.status_code == 200, f"[03]🙅隐藏走访失败,响应码错误:{hide.status_code}"
            assert hide.json()['data']['hidden'] == True, f"[03]🙅返回值不是True,实际返回值:{hide.json()}"
            self.logger.info(f"[03] ✅ 隐藏走访成功:{hide.json()['data']['hidden']}")

            # ==================== [04]删除隐藏走访 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert del_visits.status_code == 200, f"[04]🙅删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"[04]🙅删除走访失败:{del_visits.json()}"
            self.logger.info(f"[04] ✅ 删除隐藏走访成功 🏆棒棒的～:{del_visits.json()}\n")

        except AssertionError as e:
            self.logger.error(f" ☹️ 断言失败: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except IndexError as e:
            self.logger.info(f" ☹️ 索引错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
        except Exception as e:
            self.logger.info(f"错误信息:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")


    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])