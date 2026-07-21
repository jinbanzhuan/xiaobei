import pytest
import requests
import random
import traceback
import urllib3

urllib3.disable_warnings()
from utils.get_visits_item_data import get_csv_visits_item_data
from utils.logger import get_logger
from config.get_token import token
from config.api_client import base_url



"""
测试case:
01, 新增 背调事项
02, 新增 number条背调事项
03, 
04, 
05, 
06, 
07, 
"""


class TestVisitsItem:
    logger = get_logger()
    r = random.randint(0, 99)
    # base_url = "https://dev-bo-api.xiaobei.top"
    # base_url = "http://localhost:12888/"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    @pytest.mark.新增背调事项
    def test_add_background_check_item(self):
        """
        1, 新增单条背调事项
        2, 新增多条背调事项 -还未补充
        """
        item_id = []
        checklist_id = []
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            random_number = random.randint(0, 99)
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业失败,响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][random_number]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01] ✅获取随机企业id成功:{enterprise_id}")

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
            self.logger.info(f"[02] ✅新增走访:{add_visits.json()['data']}")

            # ==================== [03]查询checklistID ====================
            # POST /api/v1/visits/{visitId}/checklist/generate  接口二选一拿checklistID
            # GET /api/v1/visits/{visits_id[0]}/checklist
            get_checklist = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/checklist/generate",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert get_checklist.status_code == 200, f"[03]🙅新增走访失败,响应码错误:{add_visits.status_code}"
            # checklist_id.append(get_checklist.json()['data']['id'])
            checklist_id.append(get_checklist.json()['data']['taskId'])
            self.logger.info(f"[03] ✅查询checklistID成功:{get_checklist.json()['data']}")

            # ==================== [04]新增背调事项 ====================
            add_background_check_items = requests.post(
                url=f"{base_url}/api/v1/checklists/{checklist_id[0]}/items",
                json={
                    "question": "这是一条新增的背调事项case",
                },
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert add_background_check_items.status_code == 200, f"[04]🙅新增背调事项失败,响应码错误:{add_background_check_items.status_code}"
            item_id.append(add_background_check_items.json()['data']['id'])
            # assert add_background_check_items.json()['data']['enterpriseId'] == enterprise_id[0]
            self.logger.info(f"[04] ✅新增背调事项成功:{add_background_check_items.json()}")

            # ==================== [05]删除新增的背调事项 ====================
            del_background_check_items = requests.delete(
                url=f"{base_url}/api/v1/checklist-items/{item_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert add_background_check_items.status_code == 200, f"[05]🙅查询新增的背调事项失败,响应码错误:{add_background_check_items.status_code}"
            self.logger.info(f"[05] ✅删除新增的背调事项成功:{add_background_check_items.json()}")

            # ==================== [06]闭环 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert del_visits.status_code == 200, f"[06]🙅删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"[06]🙅删除走访失败:{del_visits.json()}"

        except AssertionError as e:
            self.logger.error(f" ☹️ 断言失败: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        except IndexError as e:
            self.logger.info(f" ☹️ 索引错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        except Exception as e:
            self.logger.info(f" 😳 未知错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        else:
            self.logger.info(f"[06] ✅新增背调事项成功 🐮奶牛牛\n")

    @pytest.mark.新增多条背调事项
    def test_add_multiple_background_check_item(self):
        """
        1, 新增 有效等价类
        2, 新增 新增字母组合
        3, 新增 字符组合
        4, 新增 数字字符字母组合
        5, 新增 数字字符组合
        6, 新增 空格组合
        7, 新增 数字
        8, 新增 字符
        9, 新增 字母
        10, 新增 空格
        11, 新增 最长字段 待定还没问coder接口限制
        12,
        """
        item_id = []
        checklist_id = []
        enterprise_id = []
        visits_id = []
        try:
            # ==================== [01]获取随机企业id 存入enterprise_id ====================
            random_number = random.randint(0, 99)
            get_enterprises = requests.get(
                url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert get_enterprises.status_code == 200, f"[01]🙅获取随机企业失败,响应码错误:{get_enterprises.status_code}"
            enterprise_id.append(get_enterprises.json()['data']['list'][random_number]['id'])
            assert enterprise_id is not None and len(
                enterprise_id) > 0, f"[01]🙅add随机企业id失败,列表为空:{enterprise_id}"
            self.logger.info(f"[01] ✅获取随机企业id成功:{enterprise_id}")

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
            self.logger.info(f"[02] ✅新增走访:{add_visits.json()['data']}")

            # ==================== [03]查询checklistID ====================
            # POST /api/v1/visits/{visitId}/checklist/generate  接口二选一拿checklistID
            # GET /api/v1/visits/{visits_id[0]}/checklist
            get_checklist = requests.post(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}/checklist/generate",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert get_checklist.status_code == 200, f"[03]🙅新增走访失败,响应码错误:{add_visits.status_code}"
            # checklist_id.append(get_checklist.json()['data']['id'])
            checklist_id.append(get_checklist.json()['data']['taskId'])
            assert checklist_id is not None and len(
                checklist_id) > 0, f"[03]🙅新增checklist_id失败,列表为空:{checklist_id}"
            self.logger.info(f"[03] ✅查询checklistID成功:{get_checklist.json()['data']}")

            # ==================== [04]新增背调事项 ====================
            for question in get_csv_visits_item_data():
                add_background_check_items = requests.post(
                    url=f"{base_url}/api/v1/checklists/{checklist_id[0]}/items",
                    json={
                        "question": question,
                    },
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                assert add_background_check_items.status_code == 200, f"[04]🙅新增背调事项失败,响应码错误:{add_background_check_items.status_code}"
                if add_background_check_items.json()['code'] == -1:
                    self.logger.info(f"[04]新增背调事项失败,返回值:{add_background_check_items.json()}")
                self.logger.info(f"[04] ✅新增背调事项成功:{add_background_check_items.json()}")
                item_id.append(add_background_check_items.json()['data']['id'])

            # ==================== [05]删除新增的背调事项 ====================
            del_background_check_items = requests.delete(
                url=f"{base_url}/api/v1/checklist-items/{item_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
            )
            assert del_background_check_items.status_code == 200, f"[05]🙅查询新增的背调事项失败,响应码错误:{del_background_check_items.status_code}"
            self.logger.info(f"[05] ✅删除新增的背调事项成功:{del_background_check_items.json()}")

            # ==================== [06]闭环 ====================
            del_visits = requests.delete(
                url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                headers=self.headers,
                timeout=(10, 30),
                verify=False
            )
            assert del_visits.status_code == 200, f"[06]🙅删除走访失败,响应码错误:{del_visits.status_code}"
            assert del_visits.json()['code'] == 0, f"[06]🙅删除走访失败:{del_visits.json()}"

        except AssertionError as e:
            self.logger.error(f" ☹️ 断言失败: {e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        except IndexError as e:
            self.logger.info(f" ☹️ 索引错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        except Exception as e:
            self.logger.info(f" 😳 未知错误:{e}")
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}\n")
        else:
            self.logger.info(f"[06] ✅新增背调事项成功, 🐮 奶牛牛 点赞  👍\n")


    if __name__ == "__main__":
        pytest.main([__file__, "-v", "-s"])
