import pytest
import requests
import random
import traceback
import time

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib3

urllib3.disable_warnings()
from config.get_token import token
from config.api_client import base_url
from config.logger import get_logger


class TestChat:
    logger = get_logger()
    r = random.randint(0, 99)
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    # @pytest.mark.xiaobei非原始接口input输入
    # def test_chat_smoke(self):
    # 
    #     try:
    #         # ==================== [01]获取指定企业id 存入enterprise_id ====================
    #         get_enterprises = requests.get(
    #             url=f"{base_url}/api/v1/enterprises?pageSize=100&page=1",
    #             headers=self.headers,
    #             timeout=(10, 30),
    #             verify=False
    #         )
    #         # 断言状态码和code为0
    #         assert get_enterprises.status_code == 200, f"[01]查询企业id失败, 状态码:{get_enterprises.status_code}, 响应:{get_enterprises.json()}"
    #         assert get_enterprises.json()['code'] == 0, f"[01]查询企业失败:{get_enterprises.json()}"
    # 
    #         # 赋值 enterprise 为企业 id
    #         enterprise = get_enterprises.json()['data']['list'][self.r]['id']
    # 
    #         # 断言是否添加成功, 列表元素是否为空
    #         assert enterprise is not None and len(
    #             enterprise) > 0, f"[01]新增企业id失败, 列表为空:{enterprise}"
    # 
    #         # 结果打印日志
    #         self.logger.info(f"[01]✅获取随机企业id: {get_enterprises.json()['data']['list'][self.r]['id']}")
    # 
    #         # ==================== [02]新增走访 ====================
    #         add_visits = requests.post(
    #             url=f"{base_url}/api/v1/visits",
    #             json={
    #                 "enterpriseId": enterprise,
    #                 "visitors": ["金阳"],
    #                 "participants": [{"name": "金阳"}],
    #                 "source": "手动录入"
    #             },
    #             headers=self.headers,
    #             timeout=(5, 30),
    #             verify=False
    #         )
    #         assert add_visits.status_code == 200, f"\n[02] 🙅 新增走访失败,响应码错误: {add_visits.status_code}"
    #         visits_id = add_visits.json()['data']['id']
    #         self.logger.info(f"[02] ✅ 新增走访成功: {add_visits.json()}")
    # 
    #         # ==================== [03]无限循环王 ====================
    # 
    #         while True:
    #             msg = input(f"🫧小北输入框（非原始接口invoke）: ")
    #             # ==================== [04]传参msg, 获取taskId ====================
    #             get_checklist = requests.post(
    #                 url=f"{base_url}/api/v1/xiaobei/invoke",
    #                 headers=self.headers,
    #                 json={
    #                     "message": msg,
    #                     "visitId": visits_id
    #                 },
    #                 timeout=(10, 30),
    #                 verify=False
    #             )
    #             assert get_checklist.status_code == 200, f"\n[03] 🔍 获取taskId失败,响应码错误: {get_checklist.status_code}"
    #             self.logger.info(f"[03] ✅ 触发checklist生成,获取taskId: {get_checklist.json()}")
    #             task_id = get_checklist.json().get('data', {}).get('taskId')
    #             if msg.lower() in ("q", "quit", "exit"):
    #                 break
    # 
    #             # ==================== [05] 查询分析结果 ====================
    #             while True:
    #                 get_analysis = requests.get(
    #                     url=f"{base_url}/api/v1/tasks/{task_id}",
    #                     headers=self.headers,
    #                     timeout=(10, 30),
    #                     verify=False
    #                 )
    #                 if get_analysis.json().get('data', {}).get('status') in ["", "pending", "processing"]:
    #                     self.logger.info(f"[05] 👀 查询中...")
    #                     time.sleep(2)
    #                 elif get_analysis.json().get('data', {}).get('status') in ["failed", "canceled"]:
    #                     self.logger.error(f"[05] ☹️ 分析失败/任务取消: {get_analysis.json()}")
    #                     break
    #                 elif get_analysis.json().get('data', {}).get('status') == "completed":
    #                     result = get_analysis.json().get('data', {}).get('result', '')
    #                     self.logger.info(f"[05] 🤖 小北: {result}\n")
    #                     break
    #                 else:
    #                     self.logger.error(f"[05] 🙅 未知状态: {get_analysis.json()}")
    # 
    #     except Exception as e:
    #         self.logger.error(f"测试异常: {e}")
    #         self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
    #         raise

    @pytest.mark.xiaobei非原生接口日常测试
    def test_chat_everyday_smoke(self):

        try:
            # ==================== [01]获取指定企业id 存入enterprise_id ====================
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

            # ==================== [02]新增走访 ====================
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
            
            # 赋值 visits 为走访id
            visits = new_visits_response.json()['data']['id']
            
            # 打印走访结果
            # self.logger.info(f"[02]列表: {enterpriseId}")
            self.logger.info(f"[02]✅新增走访成功:{new_visits_response.json()}")

            # ==================== [03]传参msg, 获取taskId ====================
            msg = "帮我生成背调报告"
            get_checklist = requests.post(
                url=f"{base_url}/api/v1/xiaobei/invoke",
                headers=self.headers,
                json={
                    "message": msg,
                    "visitId": visits
                },
                timeout=(10, 30),
                verify=False
            )
            # 断言状态码
            assert get_checklist.status_code == 200, f"\n[03]获取taskid失败，状态码: {new_visits_response.status_code}, 响应: {new_visits_response.json()}"

            # 断言响应结果
            assert get_checklist.json()['code'] == 0, f"[03]获取taskid失败:{get_checklist.json()}"
            assert get_checklist.json()['data']['taskId'] is not None, f"[03]获取taskid失败:{get_checklist.json()}"

            # 打印taskId
            task_id = get_checklist.json().get('data', {}).get('taskId')

            # 打印结果
            self.logger.info(f"[03]✅获取taskId: {get_checklist.json()}")
            
            # ==================== [04] 查询分析结果 ====================
            while True:
                get_analysis = requests.get(
                    url=f"{base_url}/api/v1/tasks/{task_id}",
                    headers=self.headers,
                    timeout=(10, 30),
                    verify=False
                )
                if get_analysis.json().get('data', {}).get('status') in ["", "pending", "processing"]:
                    self.logger.info(f"[04]🤔小北努力思考中...")
                    time.sleep(2)
                elif get_analysis.json().get('data', {}).get('status') in ["failed", "canceled"]:
                    self.logger.error(f"[04]☹️小北分析失败/任务取消: {get_analysis.json()}\n")
                    break
                elif get_analysis.json().get('data', {}).get('status') == "completed":
                    result = get_analysis.json().get('data', {}).get('result', '')
                    self.logger.info(f"[04]🫧小北对话框输入的内容:{msg}")
                    self.logger.info(f"[04]🧒小北: {result}\n")
                    break
                else:
                    self.logger.error(f"[04]🙅未知错误: {get_analysis.json()}")

        except Exception as e:
            self.logger.error(f"测试异常: {e}")
            self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
            raise

    # @pytest.mark.xiaobei原始接口input输入
    # def test_chat_xiaobei_api_smoke(self):
    #     """直连小北原生 open API，不走 /api/v1/xiaobei/invoke 封装。
    #
    #     凭据统一从 config/get_xiaobei_api.py 读取（跟 api_client / get_token 一个套路）。
    #     """
    #     api = north_app_base_url.rstrip("/")
    #     workspace_id = north_app_workspace_id
    #     agent_user_id = north_app_agent_user_id
    #     params = {"user_id": agent_user_id}
    #
    #     try:
    #         # ==================== [01] 换 access_token ====================
    #         auth = requests.post(
    #             url=f"{api}/auth/token",
    #             json={
    #                 "client_id": north_app_client_id,
    #                 "client_secret": north_app_client_secret,
    #             },
    #             timeout=(5, 30),
    #             verify=False,
    #         )
    #         assert auth.status_code == 200 and auth.json().get("code") == 0, \
    #             f"[01] 🙅 鉴权失败: {auth.status_code} {auth.text}"
    #         access_token = auth.json()["data"]["access_token"]
    #         headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    #         self.logger.info(f"[01] ✅ 拿到 access_token")
    #
    #         # ==================== [02] 多轮对话循环 ====================
    #         thread_id = ""
    #         transient = {"queued", "pending", "running"}
    #         failed = {"failed", "interrupted", "deleted", "expired"}
    #
    #         while True:
    #             msg = input(f"🫧小北输入框: ")
    #             if msg.lower() in ("q", "quit", "exit"):
    #                 break
    #
    #             # ---------- [03] 首轮 createThread / 后续轮 addBlock ----------
    #             if thread_id == "":
    #                 r = requests.post(
    #                     url=f"{api}/threads",
    #                     params=params,
    #                     headers=headers,
    #                     json={"workspace_id": workspace_id, "message": msg},
    #                     timeout=(10, 30),
    #                     verify=False,
    #                 )
    #                 assert r.status_code == 200 and r.json().get("code") == 0, \
    #                     f"[03] 🙅 createThread 失败: {r.status_code} {r.text}"
    #                 thread_id = r.json()["data"]["thread_id"]
    #                 self.logger.info(f"[03] ✅ 新建 thread: {thread_id}")
    #             else:
    #                 # addBlock 前必须等 thread 离开 running，否则上游 500
    #                 while True:
    #                     r = requests.get(f"{api}/threads/{thread_id}", params=params,
    #                                      headers=headers, timeout=(10, 30), verify=False)
    #                     s = (r.json().get("data", {}).get("status") or "").lower()
    #                     if s not in transient:
    #                         break
    #                     time.sleep(2)
    #                 r = requests.post(
    #                     url=f"{api}/threads/{thread_id}/blocks",
    #                     params=params,
    #                     headers=headers,
    #                     json={"type": "text", "data": {"content": msg}},
    #                     timeout=(10, 30),
    #                     verify=False,
    #                 )
    #                 assert r.status_code == 200 and r.json().get("code") == 0, \
    #                     f"[03] 🙅 addBlock 失败: {r.status_code} {r.text}"
    #                 self.logger.info(f"[03] ✅ addBlock 到 thread={thread_id}")
    #
    #             # ---------- [04] 轮询 thread 直到 completed ----------
    #             while True:
    #                 r = requests.get(f"{api}/threads/{thread_id}", params=params,
    #                                  headers=headers, timeout=(10, 30), verify=False)
    #                 status = (r.json().get("data", {}).get("status") or "").lower()
    #                 if status in transient:
    #                     self.logger.info(f"[04] 👀 查询中... status={status}")
    #                     time.sleep(2)
    #                     continue
    #                 if status in failed:
    #                     self.logger.error(f"[04] ☹️ 任务失败: {status}")
    #                     break
    #                 if status == "completed":
    #                     break
    #                 self.logger.error(f"[04] 🙅 未知状态: {status}")
    #                 break
    #
    #             if status != "completed":
    #                 continue
    #
    #             # ---------- [05] 分页拉 blocks 取本轮回复 ----------
    #             all_blocks, page_token = [], ""
    #             while True:
    #                 r = requests.post(
    #                     url=f"{api}/threads/{thread_id}/blocks/list",
    #                     params=params,
    #                     headers=headers,
    #                     json={"page_size": 100, "page_token": page_token},
    #                     timeout=(10, 30),
    #                     verify=False,
    #                 )
    #                 assert r.status_code == 200 and r.json().get("code") == 0, \
    #                     f"[05] 🙅 listBlocks 失败: {r.status_code} {r.text}"
    #                 data = r.json()["data"]
    #                 all_blocks.extend(data.get("items") or [])
    #                 page_token = data.get("page_token") or ""
    #                 if not page_token:
    #                     break
    #
    #             # 只在最近一条 user text 之后的当前轮里找回复
    #             turn_start = -1
    #             for i in range(len(all_blocks) - 1, -1, -1):
    #                 b = all_blocks[i]
    #                 if b.get("type") == "text" and b.get("sender") == "user":
    #                     turn_start = i
    #                     break
    #             turn = all_blocks[turn_start + 1:]
    #
    #             # 优先取非空 agent text，兜底取最后一个 Finish tool block 的 text
    #             reply = ""
    #             for b in reversed(turn):
    #                 if b.get("type") == "text" and b.get("sender") == "agent":
    #                     c = (b.get("state") or {}).get("content") or ""
    #                     if c.strip():
    #                         reply = c
    #                         break
    #             if not reply:
    #                 for b in reversed(turn):
    #                     st = b.get("state") or {}
    #                     if b.get("type") == "tool" and st.get("tool_name") == "Finish":
    #                         t = st.get("text") or ""
    #                         if t.strip():
    #                             reply = t
    #                             break
    #
    #             self.logger.info(f"[05] 🤖 小北: {reply}\n")
    #
    #     except Exception as e:
    #         self.logger.error(f"测试异常: {e}")
    #         self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
    #         raise

    # @pytest.mark.xiaobei原始接口csv
    # def test_chat_xiaobei(self):
    #     """直连小北原生 open API，**并发**灌 data/queries_data.csv 里的 question。
    #
    #     并发度 CONCURRENCY=10；每条 question 独占一个 thread（不复用上下文），
    #     原生调用链：createThread → 轮询 status → 分页读 blocks → 取当前轮回复。
    #     access_token 全局共用一次（token 有效期 >> 单次跑总耗时）。
    #     """
    #     api = north_app_base_url.rstrip("/")
    #     workspace_id = north_app_workspace_id
    #     agent_user_id = north_app_agent_user_id
    #     params = {"user_id": agent_user_id}
    #     CONCURRENCY = 5
    #
    #     try:
    #         # ==================== [01] 换 access_token ====================
    #         auth = requests.post(
    #             url=f"{api}/auth/token",
    #             json={
    #                 "client_id": north_app_client_id,
    #                 "client_secret": north_app_client_secret,
    #             },
    #             timeout=(5, 30),
    #             verify=False,
    #         )
    #         assert auth.status_code == 200 and auth.json().get("code") == 0, \
    #             f"[01] 🙅 鉴权失败: {auth.status_code} {auth.text}"
    #         access_token = auth.json()["data"]["access_token"]
    #         headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    #         self.logger.info(f"[01] ✅ 拿到 access_token")
    #
    #         # ==================== [02] 加载 CSV 问题列表 ====================
    #         questions = get_csv_queries_data()
    #         total = len(questions)
    #         self.logger.info(f"[02] ✅ 从 CSV 加载 question 数量: {total}, 并发数: {CONCURRENCY}")
    #
    #         transient = {"queued", "pending", "running"}
    #         failed = {"failed", "interrupted", "deleted", "expired"}
    #
    #         # ==================== 网络异常 / 5xx 自动重试助手 ====================
    #         def _do_request(method, url, *, phase, idx, max_attempts=10, **kwargs):
    #             """带网络异常 + 5xx 自动重试的 HTTP 调用。
    #
    #             - ConnectionError / Timeout：等 10s 后重试
    #             - HTTP 5xx：              等 30s 后重试（上游瞬时错误）
    #             - 其它响应：              直接返回给调用方判定 code / data
    #
    #             max_attempts 用尽仍失败 → 返回 None，调用方转成 run_one 的 err 上抛。
    #             每次 wait 期间用 logger.warning 打点，保持 235 条整体可观测。
    #             """
    #             for attempt_number in range(1, max_attempts + 1):
    #                 try:
    #                     resp = requests.request(method, url, verify=False, **kwargs)
    #                 except (requests.ConnectionError, requests.Timeout) as e:
    #                     self.logger.warning(
    #                         f"[{phase}] 🌐 idx={idx} 网络异常: {type(e).__name__} - {e},"
    #                         f"第 {attempt_number} 次重试,等 10 秒..."
    #                     )
    #                     time.sleep(10)
    #                     continue
    #                 if resp.status_code >= 500:
    #                     self.logger.warning(
    #                         f"[{phase}] ⚠️ idx={idx} 服务端 {resp.status_code},"
    #                         f"第 {attempt_number} 次重试,等 30 秒..."
    #                     )
    #                     time.sleep(30)
    #                     continue
    #                 return resp
    #             return None
    #
    #         # ==================== [03] 单条 question 完整链路 ====================
    #         def run_one(idx, msg):
    #             """createThread → 轮询 → 读回复。返回 (idx, msg, thread_id, reply, err)。
    #
    #             每条 question 独占一个 thread，避免共享 thread_id 触发 addBlock 竞态。
    #             单条内部异常不抛出，转成 err 字符串返回给主线程统一日志，
    #             保证一条挂了不影响其它 9 个 worker。
    #             """
    #             msg = (msg or "").strip()
    #             if not msg:
    #                 return idx, msg, "", "", "empty question"
    #             t0 = time.time()
    #             try:
    #                 # createThread（首轮直接建）
    #                 r = _do_request(
    #                     "POST", f"{api}/threads",
    #                     phase="03", idx=idx,
    #                     params=params, headers=headers,
    #                     json={"workspace_id": workspace_id, "message": msg},
    #                     timeout=(10, 60),
    #                 )
    #                 if r is None:
    #                     return idx, msg, "", "", "createThread 重试用尽"
    #                 if r.status_code != 200 or r.json().get("code") != 0:
    #                     return idx, msg, "", "", f"createThread {r.status_code} {r.text[:200]}"
    #                 thread_id = r.json()["data"]["thread_id"]
    #
    #                 # 轮询直到 completed / 失败终态
    #                 status = ""
    #                 while True:
    #                     r = _do_request(
    #                         "GET", f"{api}/threads/{thread_id}",
    #                         phase="04", idx=idx,
    #                         params=params, headers=headers,
    #                         timeout=(10, 30),
    #                     )
    #                     if r is None:
    #                         return idx, msg, thread_id, "", "getStatus 重试用尽"
    #                     status = (r.json().get("data", {}).get("status") or "").lower()
    #                     if status in transient:
    #                         time.sleep(2)
    #                         continue
    #                     break
    #                 if status != "completed":
    #                     return idx, msg, thread_id, "", f"status={status}"
    #
    #                 # 分页拉 blocks
    #                 all_blocks, page_token = [], ""
    #                 while True:
    #                     r = _do_request(
    #                         "POST", f"{api}/threads/{thread_id}/blocks/list",
    #                         phase="05", idx=idx,
    #                         params=params, headers=headers,
    #                         json={"page_size": 100, "page_token": page_token},
    #                         timeout=(10, 30),
    #                     )
    #                     if r is None:
    #                         return idx, msg, thread_id, "", "listBlocks 重试用尽"
    #                     if r.status_code != 200 or r.json().get("code") != 0:
    #                         return idx, msg, thread_id, "", f"listBlocks {r.status_code} {r.text[:200]}"
    #                     data = r.json()["data"]
    #                     all_blocks.extend(data.get("items") or [])
    #                     page_token = data.get("page_token") or ""
    #                     if not page_token:
    #                         break
    #
    #                 # 定位当前轮：最近一条 user text 之后
    #                 turn_start = -1
    #                 for i in range(len(all_blocks) - 1, -1, -1):
    #                     b = all_blocks[i]
    #                     if b.get("type") == "text" and b.get("sender") == "user":
    #                         turn_start = i
    #                         break
    #                 turn = all_blocks[turn_start + 1:]
    #
    #                 # 优先取非空 agent text；兜底取最后一个 Finish tool block 的 text
    #                 reply = ""
    #                 for b in reversed(turn):
    #                     if b.get("type") == "text" and b.get("sender") == "agent":
    #                         c = (b.get("state") or {}).get("content") or ""
    #                         if c.strip():
    #                             reply = c
    #                             break
    #                 if not reply:
    #                     for b in reversed(turn):
    #                         st = b.get("state") or {}
    #                         if b.get("type") == "tool" and st.get("tool_name") == "Finish":
    #                             t = st.get("text") or ""
    #                             if t.strip():
    #                                 reply = t
    #                                 break
    #
    #                 elapsed = time.time() - t0
    #                 return idx, msg, thread_id, reply, f"ok in {elapsed:.1f}s"
    #             except Exception as ex:
    #                 return idx, msg, "", "", f"exception: {ex}"
    #
    #         # ==================== [04] 并发执行 ====================
    #         done = 0
    #         done_lock = Lock()
    #         with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    #             futures = {
    #                 ex.submit(run_one, i + 1, q): (i + 1, q)
    #                 for i, q in enumerate(questions)
    #             }
    #             for fut in as_completed(futures):
    #                 idx, msg, thread_id, reply, note = fut.result()
    #                 with done_lock:
    #                     done += 1
    #                     tag = thread_id[:8] if thread_id else "-"
    #                     if reply:
    #                         self.logger.info(
    #                             f"[{done}/{total}] ✅ idx={idx} thread={tag} {note}\n"
    #                             f"    Q: {msg}\n"
    #                             f"    A: {reply}\n"
    #                         )
    #                     else:
    #                         self.logger.error(
    #                             f"[{done}/{total}] ❌ idx={idx} thread={tag} {note}\n"
    #                             f"    Q: {msg}\n"
    #                         )
    #
    #     except Exception as e:
    #         self.logger.error(f"测试异常: {e}")
    #         self.logger.error(f"堆栈信息: \n{traceback.format_exc()}")
    #         raise


if __name__ == "__main__":
    test = TestChat()
    # test.test_chat_xiaobei()  # 原生（批量灌 CSV）
    # test.test_chat_xiaobei_api_smoke()    # 原生（交互式 input）
    # test.test_chat_smoke()                # 走后端封装
    test.test_chat_everyday_smoke()
