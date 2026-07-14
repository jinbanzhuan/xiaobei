import traceback
# import random
import time
import pytest
import requests

from config.get_token import token
from config.api_client import base_url
from config.logger import get_logger


class TestTimeAnalysis:
    # r = random.randint(0, 99)
    # base_url = "https://dev-bo-api.xiaobei.top"
    # base_url = "http://localhost:12888/"
    logger = get_logger()
    feishu_url = "https://fcn6bo5q7kmm.feishu.cn/minutes/obcnn93hqjwgf17o1l6x4ys8"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # ==================== 飞书妙计 ====================
    # 	思特威（上海）电子科技股份有限公司：https://fcn6bo5q7kmm.feishu.cn/minutes/obcnn9zfzlfv674772q6u2sp
    # 	上海米哈游网络科技股份有限公司：https://fcn6bo5q7kmm.feishu.cn/minutes/obcnn93hqjwgf17o1l6x4ys8

    # ==================== 走访公司 ====================
    # 思特威（上海）电子科技股份有限公司:5cceb7a9-c6dd-4ef7-9d82-32e7f76285ad
    # 上海米哈游网络科技股份有限公司:0e9128e8-af58-4d0d-9b7e-b818a1dac7cc

    def test_analysis(self):
        """
        1, 耗时分析
        """

        for cycle in range(1, 2):

            self.logger.info(f"========== 第 {cycle} 次 ♻️ 循环开始 ==========")

            item_id = []
            checklist_id = []
            enterprise_id = []
            visits_id = []
            tasks_id = []
            start_time = time.time()


            try:
                # ==================== [01]获取指定企业id 存入enterprise_id ====================
                target_enterprise_name = "上海米哈游网络科技股份有限公司"

                get_enterprises = requests.get(
                    url=f"{base_url}/api/v1/enterprises?pageSize=1000&page=1",
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert get_enterprises.status_code == 200, f"\n[01] 🙅 获取企业列表失败,响应码错误: {get_enterprises.status_code}"

                enterprises_list = get_enterprises.json()['data']['list']
                matched = next(
                    (e for e in enterprises_list if e.get('name') == target_enterprise_name),
                    None
                )
                assert matched is not None, f"\n[01] 🙅 未在企业列表中找到目标企业: {target_enterprise_name}"

                enterprise_id.append(matched['id'])
                assert enterprise_id is not None and len(
                    enterprise_id) > 0, f"\n[01] 🙅 add指定企业id失败,列表为空: {enterprise_id}"
                self.logger.info(f"[01] ✅ 获取指定企业id成功: {target_enterprise_name} -> {enterprise_id}")



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
                    timeout=(5, 30),
                    verify=False
                )
                assert add_visits.status_code == 200, f"\n[02] 🙅 新增走访失败,响应码错误: {add_visits.status_code}"
                assert add_visits.json()['data']['enterpriseId'] == enterprise_id[
                    0], f"\n[02] 🙅 企业id不一致,返回值enterpriseId: {add_visits.json()['data']['enterpriseId']},列表enterpriseId: {enterprise_id[0]}"
                visits_id.append(add_visits.json()['data']['id'])
                self.logger.info(f"[02] ✅ 新增走访: {add_visits.json()['data']}")

                # ==================== [03]触发checklist生成,获取taskId ====================
                get_checklist = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/checklist/generate",
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert get_checklist.status_code == 200, f"\n[03] 🙅 获取taskId失败,响应码错误: {get_checklist.status_code}"
                checklist_id.append(get_checklist.json()['data']['taskId'])
                self.logger.info(f"[03] ✅ 触发checklist生成,获取taskId: {get_checklist.json()['data']}")

                # ==================== [04]新增背调事项 ====================
                add_background_check_items = requests.post(
                    url=f"{base_url}/api/v1/checklists/{checklist_id[0]}/items",
                    json={
                        "question": "公司的合规与ESG有没有随时引爆的雷？",
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert add_background_check_items.status_code == 200, f"\n[04] 🙅 新增背调事项失败,响应码错误: {add_background_check_items.status_code}"
                item_id.append(add_background_check_items.json()['data']['id'])
                self.logger.info(f"[04] ✅ 新增背调事项成功: {add_background_check_items.json()}")

                # ==================== [05]获取taskid ====================
                get_task_id = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/report/generate",
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert get_task_id.status_code == 200, f"\n[05] 🙅 获取taskid失败,响应码错误: {get_task_id.status_code}"
                self.logger.info(f"[05] ✅ 获取taskid成功: {get_task_id.json()}")
                tasks_id.append(get_task_id.json()['data']['taskId'])

                # ==================== [06]异步任务状态轮询 ====================
                attempt = 0

                while True:
                    attempt += 1
                    try:
                        get_result = requests.get(
                            url=f"{base_url}/api/v1/tasks/{tasks_id[0]}",
                            headers=self.headers,
                            timeout=(5, 30),
                            verify=False
                        )
                    except (requests.ConnectionError, requests.Timeout) as e:
                        self.logger.warning(
                            f"[06] 🌐 网络异常: {type(e).__name__} - {e},第 {attempt} 次重试,等 10 秒..."
                        )
                        time.sleep(10)
                        continue
                    if get_result.status_code >= 500:
                        self.logger.warning(
                            f"[06] ⚠️ 服务端 {get_result.status_code},第 {attempt} 次重试,等 30 秒..."
                        )
                        time.sleep(30)
                        continue

                    assert get_result.status_code == 200, f"\n[06] 🙅 查询taskid失败,响应码错误: {get_result.status_code}"

                    elapsed_time = time.time() - start_time

                    if get_result.json()['data']['result'] != '':
                        self.logger.info(
                            f"[06] ✅ 当前接口状态 {get_result.json()['data']['status']},第 {cycle} 次 ♻️ 循环 - 报告分析成功,♻️ 循环 {attempt} 次, ⏳ 耗时 {elapsed_time:.2f}秒")
                        break
                    elif get_result.json()["data"]["status"] == "failed" or get_result.json()["data"][
                        "status"] == "canceled":
                        self.logger.info(f"任务被取消或者分析失败: {get_result.json()['data']['status']}")
                        break

                    self.logger.info(
                        f"[06] 👀 当前接口状态 {get_result.json()['data']['status']}, ⏳ 耗时 {elapsed_time:.2f}秒")
                    time.sleep(2)

                # ==================== [07]扭转状态checklist ====================
                checklists = requests.put(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                    json={
                        "status": "checklist"
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert checklists.status_code == 200, f"\n[07] 🙅 响应码错误: {checklists.status_code}"
                assert checklists.json()['data'][
                           'status'] == "checklist", f"\n[07] 🙅 状态非checklist,实际状态: {checklists.json()['data']['status']}"
                assert checklists.json()['data']['enterpriseId'] == enterprise_id[
                    0], f"\n[07] 🙅 企业id不一致,返回值enterpriseId: {checklists.json()['data']['enterpriseId']},列表enterpriseId: {enterprise_id[0]}"
                self.logger.info(f"[07] ✅ 准备阶段-沟通清单: {checklists.json()['data']}")

                # ==================== [08]扭转状态visiting ====================
                visitings = requests.put(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                    json={
                        "status": "visiting"
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )

                assert visitings.status_code == 200, f"\n[08] 🙅 响应码错误: {visitings.status_code}"
                assert visitings.json()['data'][
                           'status'] == "visiting", f"\n[08] 🙅 状态非visiting,实际状态: {visitings.json()['data']['status']}"
                assert visitings.json()['data']['enterpriseId'] == enterprise_id[
                    0], f"\n[08] 🙅 企业id不一致,返回值enterpriseId: {visitings.json()['data']['enterpriseId']},列表enterpriseId: {enterprise_id[0]}"
                self.logger.info(f"[08] ✅ 准备阶段-走访中: {visitings.json()['data']}")

                # ==================== [09]扭转状态confirmed ====================
                confirmed = requests.put(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                    json={
                        "status": "confirmed"
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )

                assert confirmed.status_code == 200, f"\n[09] 🙅 响应码错误: {confirmed.status_code}"
                assert confirmed.json()['data'][
                           'status'] == "confirmed", f"\n[09] 🙅 状态非confirmed,实际状态: {confirmed.json()['data']['status']}"
                assert confirmed.json()['data']['enterpriseId'] == enterprise_id[
                    0], f"\n[09] 🙅 企业id不一致,返回值enterpriseId: {confirmed.json()['data']['enterpriseId']},列表enterpriseId: {enterprise_id[0]}"
                self.logger.info(f"[09] ✅ 结束阶段-记录走访要点: {confirmed.json()['data']}")

                # ==================== [10]上传走访材料成功 ====================
                add_attachments = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/attachments",
                    json={
                        "type": "url",
                        "url": self.feishu_url,
                        "name": "飞书妙记"
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                # 断言状态码和响应结果
                assert add_attachments.status_code == 200, f"\n[10] 🙅 响应码错误: {add_attachments.status_code}"
                assert add_attachments.json()['data'][
                           'url'] == self.feishu_url, f"[10] 🙅 上传材料url错误,返回值: {add_attachments.json()['data']['url']},列表url: {self.feishu_url}"
                self.logger.info(f"[10] ✅ 上传走访材料成功: {add_attachments.json()['data']}")

                # ==================== [11]贴妙记/文档/智能纪要,拉内容写进visit ====================
                add_parse = requests.post(
                    url=f"{base_url}/api/v1/minutes/parse",
                    json={
                        "enterpriseId": enterprise_id[0],
                        "visitId": visits_id[0],
                        "rawContent": self.feishu_url
                    },
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert add_parse.status_code == 200, f"\n[11] 🙅 响应码错误: {add_parse.status_code}"
                assert add_parse.json()['data'][
                           'taskId'] is not None, f"\n[11] 🙅 tasksId为空, 返回值: {add_parse.json()}"
                tasks_id.append(add_parse.json()['data']['taskId'])
                self.logger.info(f"[11] ✅ 内容写入visits成功: {add_parse.json()['data']}")

                # ===================== [12]查询解析结果 status==completed ====================
                """
                pending	    任务已创建,还没被 worker 消费	继续轮询
                processing	worker 正在解析妙记、拉转写、写 visit	继续轮询
                completed	妙记解析完成,已写入 visits.raw_minutes_content 等字段	可以继续调用 /api/v1/visits/{visitId}/analyze
                failed	    妙记解析失败,比如权限不足、链接无效、转写不可读、查重等	直接失败,打印 error
                canceled	任务被取消,通常是同一个 visit 又发起了新的 parse,旧任务被 supersede
                """
                attempt_number = 0

                while True:
                    attempt_number += 1
                    try:
                        parse_result = requests.get(
                            url=f"{base_url}/api/v1/minutes/parse-result/{tasks_id[1]}",
                            headers=self.headers,
                            timeout=(5, 30),
                            verify=False
                        )
                    except (requests.ConnectionError, requests.Timeout) as e:
                        self.logger.warning(
                            f"[12] 🌐 网络异常: {type(e).__name__} - {e},第 {attempt_number} 次重试,等 10 秒..."
                        )
                        time.sleep(10)
                        continue
                    if parse_result.status_code >= 500:
                        self.logger.warning(
                            f"[12] ⚠️ 服务端 {parse_result.status_code},第 {attempt_number} 次重试,等 30 秒..."
                        )
                        time.sleep(30)
                        continue

                    assert parse_result.status_code == 200, f"\n[12] 🙅 响应码错误: {parse_result.status_code}"
                    assert parse_result.json()['status'] in ["", "pending", "processing", "completed", "failed",
                                                             "canceled"], f"\n[12] 🙅 状态不对,返回值: {parse_result.json()}"

                    elapsed_time = time.time() - start_time

                    if parse_result.json()['status'] == "completed":
                        self.logger.info(
                            f"[12] ✅ 当前接口状态 {parse_result.json()['status']},第 {cycle} 次 ♻️ 循环 - 报告分析成功,♻️ 循环 {attempt_number} 次, ⏳ 耗时 {elapsed_time:.2f}秒")
                        break
                    elif parse_result.json()["status"] == "failed" or parse_result.json()["status"] == "canceled":
                        raise AssertionError(f"任务被取消或者分析失败: {parse_result.json()}")
                    self.logger.info(
                        f"[12] ✅ 当前接口状态 {parse_result.json()['status']}, ⏳ 耗时 {elapsed_time:.2f}秒")
                    time.sleep(2)

                # ===================== [13]触发ai分析 ====================
                add_analyze = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/analyze",
                    json={},
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert add_analyze.status_code == 200, f"\n[13] 🙅 响应码错误: {add_analyze.status_code}"
                tasks_id.append(add_analyze.json()['data']['taskId'])
                self.logger.info(f"[13] ✅ 触发ai分析成功: {add_analyze.json()['data']}")

                # ===================== [14]查询解析结果 status==processing ====================
                """
                pending	    任务已创建,还没被 worker 消费	继续轮询
                processing	worker 正在解析妙记、拉转写、写 visit	继续轮询
                completed	妙记解析完成,已写入 visits.raw_minutes_content 等字段	可以继续调用 /api/v1/visits/{visitId}/analyze
                failed	    妙记解析失败,比如权限不足、链接无效、转写不可读、查重等	直接失败,打印 error
                canceled	任务被取消,通常是同一个 visit 又发起了新的 parse,旧任务被 supersede
                """
                attempt_numbers = 0

                while True:
                    attempt_numbers += 1
                    try:
                        get_tasks = requests.get(
                            url=f"{base_url}/api/v1/minutes/parsed/{tasks_id[2]}",
                            headers=self.headers,
                            timeout=(5, 30),
                            verify=False
                        )
                    except (requests.ConnectionError, requests.Timeout) as e:
                        self.logger.warning(
                            f"[14] 🌐 网络异常: {type(e).__name__} - {e},第 {attempt_numbers} 次重试,等 10 秒..."
                        )
                        time.sleep(10)
                        continue
                    if get_tasks.status_code >= 500:
                        self.logger.warning(
                            f"[14] ⚠️ 服务端 {get_tasks.status_code},第 {attempt_numbers} 次重试,等 30 秒..."
                        )
                        time.sleep(30)
                        continue

                    assert get_tasks.status_code == 200, f"\n[14] 🙅 响应码错误: {get_tasks.status_code}"
                    assert get_tasks.json()['data']['status'] in ["", "pending", "processing", "completed", "failed",
                                                                  "canceled"], f"\n[14] 🙅 状态不对,返回值: {get_tasks.json()}"

                    elapsed_time = time.time() - start_time

                    if get_tasks.json()["data"]["status"] == "completed":
                        self.logger.info(
                            f"[14] ✅ 当前接口状态 {get_tasks.json()['data']['status']},第 {cycle} 次 ♻️ 循环 - 报告分析成功,♻️ 循环 {attempt_numbers} 次, ⏳ 耗时 {elapsed_time:.2f}秒")
                        break
                    elif get_tasks.json()["data"]["status"] == "failed" or get_tasks.json()["data"][
                        "status"] == "canceled":
                        raise AssertionError(f"任务被取消或者分析失败: {get_tasks.json()['data']['status']}")

                    self.logger.info(
                        f"[14] 👀 当前接口状态 {get_tasks.json()['data']['status']}, ⏳ 耗时 {elapsed_time:.2f}秒")
                    time.sleep(2)

                # ===================== [15]AI提取画像更新 ====================
                add_profile_updates = requests.get(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/profile-updates",
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                # 断言状态码和响应结果
                assert add_profile_updates.status_code == 200, f"\n[15] 🙅 响应码错误: {add_profile_updates.status_code}"
                assert add_profile_updates.json()['data']['visitId'] == visits_id[
                    0], f"\n[15] 🙅 画像更新visitId错误,返回值: {add_profile_updates.json()['data']['visitId']},列表visitId: {visits_id[0]}"
                self.logger.info(f"[15] ✅ AI提取的画像更新成功: {add_profile_updates.json()['data']}")

                # ===================== [16]提交走访 ====================
                add_submit = requests.post(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}/submit",
                    json={},
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert add_submit.status_code == 200, f"\n[16] 🙅 响应码错误: {add_submit.status_code}"
                assert add_submit.json()['data']['visitId'] == visits_id[
                    0], f"\n[16] 🙅 提交走访visitId错误,返回值: {add_submit.json()['data']['visitId']},列表visitId: {visits_id[0]}"
                self.logger.info(f"[16] ✅ 提交走访成功: {add_submit.json()['data']}")

                # ===================== [17]扭转状态submitted ====================
                commit_visits = requests.put(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                    json={"status": "submitted"},
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                # 断言状态码和响应结果
                assert commit_visits.status_code == 200, f"\n[17] 🙅 响应码错误: {commit_visits.status_code}"
                assert commit_visits.json()['data'][
                           'status'] == "submitted", f"\n[17] 🙅 状态错误,返回值: {commit_visits.json()['data']['status']}"
                self.logger.info(f"[17] ✅ 跟进阶段-需求处理与任务分配: {commit_visits.json()['data']}")

                # ==================== [18]删除走访 ====================
                del_response = requests.delete(
                    url=f"{base_url}/api/v1/visits/{visits_id[0]}",
                    headers=self.headers,
                    timeout=(5, 30),
                    verify=False
                )
                assert del_response.status_code == 200, f"\n[18] 🙅 响应码错误: {del_response.status_code}"
                assert del_response.json()['code'] == 0, f"\n[18] 🙅 删除走访失败,返回值: {del_response.json()}"
                self.logger.info(f"[18] ✅ 删除成功: {del_response.json()}\n")
                self.logger.info(f"========== 妙记解析结果 第 {cycle} 次 ♻️ 循环结束 ==========\n")

            except Exception as e:
                self.logger.error(f"任务list: {tasks_id}")
                self.logger.error(f"走访list: {visits_id}")
                self.logger.error(f"企业list: {enterprise_id}")
                self.logger.error(f"第 {cycle} 次 测试异常: {e}")
                self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
                self.logger.error(f"========== 第 {cycle} 次 ♻️ 循环异常结束 ==========\n")
                continue

    if __name__ == "__main__":
        pytest.main([__file__])
