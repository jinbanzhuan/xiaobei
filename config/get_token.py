import base64
import json
import os
import time

from config.logger import get_logger

logger = get_logger(__name__)

# ============================================
# 小贝 token 获取
# 优先级:
#   1. .env.local 里显式配的 XIAOBEI_TOKEN(直接使用,不做过期检查)
#   2. .env.local 里的 NORTH_NOVA_BO_AUTH JSON(检查 expiresAt,没过期就用)
#   3. 本文件内嵌的 _DEFAULT_AUTH_JSON(仓库 seed, 保证 git clone 后开箱即用)
#   4. Playwright 打开浏览器 → 飞书扫码 → 从 localStorage 抓 token → 写回 .env.local
#
# 首次使用:会弹出 Chromium 窗口让你扫码,扫完自动关闭
# 之后使用:浏览器数据被缓存到 BROWSER_DATA_DIR,大概率无需重新扫码
# ============================================

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")

# ============================================
# 内嵌 seed token —— 用于 git pull 后无 .env.local 也能跑
# ⚠️ 是真 JWT, 到 expiresAt 之后会自动失效, 届时代码会自动走 Playwright 分支重新扫码
# ⚠️ 不要把过期时间很长的长期 token 放这里; 出问题请重新扫码后手动替换
# ============================================
_DEFAULT_AUTH_JSON = {
    "userId": "910c4f2d-5734-4d54-8cb9-8c3c64b66d13",
    "tenantId": "d923297c-5912-494b-927c-0000c70ee8e4",
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODQyNzk2MDMsImlhdCI6MTc4MzY3NDgwMywidGVuYW50X2lkIjoiZDkyMzI5N2MtNTkxMi00OTRiLTkyN2MtMDAwMGM3MGVlOGU0IiwidXNlcl9pZCI6IjkxMGM0ZjJkLTU3MzQtNGQ1NC04Y2I5LThjM2M2NGI2NmQxMyJ9.BPG7058Hom_aNiEhYd32JUNEH5_cbwf-d4yQFT1yvPw",
    "expiresAt": 1784279603,
    "username": "金阳",
}

# 浏览器数据持久化目录:飞书 cookie / 小贝 session 都在这里
# 一次扫码后,后续启动是"已登录"状态,不用再扫
BROWSER_DATA_DIR = os.path.expanduser("~/.xiaobei_playwright_data")

# 小贝管理后台前端地址(飞书扫码入口)
# 注意: dev-bo.xiaobei.top 对某些组织会提示"暂不支持当前组织", 用 dev.xiaobei.top 打开登录页更友好
XIAOBEI_LOGIN_URL = "https://dev.xiaobei.top"

# token 真正落在哪个 origin 的 localStorage
# 用 dev-bo.xiaobei.top(老前端): 加载后只显示一张静态错误页("暂不支持当前组织"),
#   但页面稳定不跳转, 且 localStorage 里 north_nova_bo_auth 一定会被写入 —— 稳
# ⚠️ 不要改成 chj.xiaobei.top: 它自己有跳转逻辑, 会被我们的定时 reload 组合成死循环刷屏
TOKEN_ORIGIN = "https://dev-bo.xiaobei.top"

# Local Storage 里存 token 的 key
AUTH_STORAGE_KEY = "north_nova_bo_auth"

# token 剩余寿命小于这个秒数,就认为该刷新了(默认 60 秒)
TOKEN_REFRESH_THRESHOLD = 60

# 打开浏览器后等用户完成登录的超时时间(毫秒),默认 3 分钟
LOGIN_TIMEOUT_MS = 180000


def get_env_value(key):
    """
    从 .env.local 里读取指定配置
    优先级: 系统环境变量 > .env.local 文件
    .env.local 不存在时静默返回空串, 交给上层走内嵌 seed / 浏览器兜底
    """
    if os.getenv(key):
        return os.getenv(key)

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "" or line.startswith("#") or "=" not in line:
                    continue

                env_key, env_value = line.split("=", 1)
                if env_key.strip() == key:
                    return env_value.strip().strip('"').strip("'")

        return ""

    except FileNotFoundError:
        return ""
    except Exception as e:
        logger.error(f"读取.env.local失败: {e}")
        return ""


def update_env_local(key, value):
    """
    更新 .env.local 里的某个 key(不存在则追加; 文件不存在则新建)
    Playwright 抓到新 token 后自动写回,下次跑不用重开浏览器
    """
    lines = []
    found = False
    try:
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{key}="):
                        lines.append(f"{key}={value}\n")
                        found = True
                    else:
                        lines.append(line)
        except FileNotFoundError:
            # 首次跑, .env.local 还不存在, 直接新建
            pass

        if not found:
            if lines and not lines[-1].endswith("\n"):
                lines.append("\n")
            lines.append(f"{key}={value}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        logger.warning(f"⚠️ 写入 .env.local 失败(不影响本次运行): {e}")


def _parse_auth_json(auth_text):
    """安全解析 NORTH_NOVA_BO_AUTH 的 JSON 字符串"""
    if not auth_text:
        return None
    try:
        return json.loads(auth_text)
    except Exception as e:
        logger.warning(f"⚠️ 解析 NORTH_NOVA_BO_AUTH 失败: {e}")
        return None


def _is_auth_valid(auth_json):
    """判断 auth JSON 是否有 token 且未过期"""
    if not auth_json:
        return False
    if not auth_json.get("accessToken"):
        return False
    expires_at = auth_json.get("expiresAt", 0)
    remaining = expires_at - int(time.time())
    return remaining > TOKEN_REFRESH_THRESHOLD


def _parse_jwt_payload(jwt_token):
    """
    从 JWT 字符串里解出 payload 字典 (base64url 解码中间段)
    典型字段: exp / iat / tenant_id / user_id
    解析失败返回空 dict
    """
    if not jwt_token or jwt_token.count(".") != 2:
        return {}
    payload_b64 = jwt_token.split(".")[1]
    padding = "=" * (-len(payload_b64) % 4)  # base64url 常常没 padding, 补齐
    try:
        return json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
    except Exception as e:
        logger.warning(f"⚠️ 解析 JWT payload 失败(不影响): {e}")
        return {}


def _clean_stale_singleton_lock():
    """
    清理僵尸 SingletonLock: 如果 lock 指向的 pid 已经不存在, 就删除它
    典型场景: 上次 Playwright 意外中止, 留下 lock 文件, 导致下次 launch 时
    Chrome for Testing 认为"已有实例在跑"并拒绝启动, 报 TargetClosedError
    """
    lock_path = os.path.join(BROWSER_DATA_DIR, "SingletonLock")
    if not os.path.islink(lock_path):
        return
    try:
        target = os.readlink(lock_path)  # 例如 "Mac.lan-34914"
        pid = int(target.rsplit("-", 1)[-1])
        try:
            os.kill(pid, 0)  # signal 0: 只探测进程是否存在, 不真的发信号
            # 进程还活着, 说明确实有实例在跑, 保留 lock, 让 Playwright 自己报错更明确
        except ProcessLookupError:
            # 进程已不存在, 是僵尸 lock, 一并清理三个 Singleton 相关文件
            for name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                try:
                    os.remove(os.path.join(BROWSER_DATA_DIR, name))
                except FileNotFoundError:
                    pass
            logger.info(f"🧹 已清理僵尸 SingletonLock (pid={pid} 不存在)")
    except Exception as e:
        # 解析失败保守起见不动, 让 Playwright 自己处理
        logger.warning(f"⚠️ 解析 SingletonLock 失败(不影响): {e}")


def _fetch_token_via_browser():
    """
    用 Playwright 打开浏览器,等用户扫码登录,从 localStorage 抓 token
    返回完整的 auth JSON 字典(含 accessToken / expiresAt / userId 等)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise Exception(
            "❌ 未安装 Playwright,请先运行:\n"
            "   pip install playwright\n"
            "   playwright install chromium"
        )

    # 判断是不是首次:如果浏览器数据目录不存在,肯定要显示窗口让用户扫码
    is_first_time = not os.path.exists(BROWSER_DATA_DIR)

    if is_first_time:
        logger.info("🌐 首次登录,即将打开 Chromium 浏览器,请用飞书扫码...")
    else:
        logger.info("🌐 尝试用缓存的浏览器数据登录...")
        # 清理上次可能残留的僵尸 SingletonLock (Chromium 崩溃/被强杀 时会留)
        _clean_stale_singleton_lock()

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,  # 始终显示窗口,以防 cookie 过期需要重新扫码
        )

        # 【第三重兜底】: 监听 xiaobei.top 域名下所有请求, 抓第一个 Authorization Bearer
        # 有些前端(比如 dev.xiaobei.top 新前端)只把 token 存 cookie/内存, 不落 localStorage
        # 只要页面发过一次带 token 的 API 请求, 我们就能拦到
        captured_token = {"value": None}

        def _on_request(request):
            if captured_token["value"]:
                return
            if "xiaobei.top" not in request.url:
                return
            # Playwright 里 header key 全部小写
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                token_val = auth[len("Bearer "):].strip()
                if token_val and token_val.count(".") == 2:  # 简单校验是不是 JWT
                    captured_token["value"] = token_val
                    logger.info(f"🔍 从 API 请求头抢到 Bearer token (url={request.url[:80]}...)")

        ctx.on("request", _on_request)

        # tab 1: 用户扫码用, 打开友好的登录页
        login_page = ctx.new_page()
        login_page.goto(XIAOBEI_LOGIN_URL)

        # tab 2: 只为了能读 TOKEN_ORIGIN 的 localStorage
        # dev-bo.xiaobei.top(老前端)加载后即使显示错误页, 也会把 token 写进自己 origin 的 localStorage
        token_page = ctx.new_page()
        try:
            token_page.goto(TOKEN_ORIGIN)
        except Exception:
            pass  # 加载失败也没关系, 只要 localStorage 能读就行

        # 轮询 token_page.localStorage (+ 同时探测 login_page)
        # 每 1 秒读一次, 每 5 秒 reload 一次 token_page 让 SPA 有机会重新拉 token
        # 用 Python 外层 while 而不是 page.wait_for_function, 因为跨 origin 跳转会
        # destroy execution context, wait_for_function 会挂死
        # 【双兜底】: 同时从 login_page 和 token_page 读 north_nova_bo_auth,
        #           任一读到即用, 防止某个 origin 因错误页/组织限制没写 localStorage
        # 【诊断】: URL 变化时打印当前 origin 下的所有 localStorage key
        deadline = time.time() + LOGIN_TIMEOUT_MS / 1000
        auth_str = None
        last_login_url = ""
        last_reload = time.time()
        RELOAD_INTERVAL = 5

        def _read_auth(page):
            try:
                return page.evaluate(
                    f"() => localStorage.getItem('{AUTH_STORAGE_KEY}')"
                )
            except Exception:
                return None

        while time.time() < deadline:
            # 打印登录 tab 的 URL 变化 + 该 origin 下的 localStorage keys
            try:
                cur_url = login_page.url
                if cur_url != last_login_url:
                    logger.info(f"🔍 登录页跳转: {cur_url}")
                    last_login_url = cur_url
                    try:
                        keys = login_page.evaluate("() => Object.keys(localStorage)")
                        logger.info(f"   [DEBUG] login_page localStorage keys: {keys}")
                    except Exception:
                        pass
            except Exception:
                pass

            # 双兜底: 从两个 tab 分别读 north_nova_bo_auth
            auth_str = _read_auth(token_page) or _read_auth(login_page)
            if auth_str:
                # 顺便记一下 token 是从哪个 tab 读到的, 方便后续简化
                src = "token_page" if _read_auth(token_page) else "login_page"
                logger.info(f"   [DEBUG] 从 {src} 读到 {AUTH_STORAGE_KEY}")
                break

            # 第三重兜底: 监听器抢到了 Bearer, 用 JWT payload 合成 auth JSON
            if captured_token["value"]:
                token_val = captured_token["value"]
                payload = _parse_jwt_payload(token_val)
                if payload.get("exp"):
                    auth_synth = {
                        "userId": payload.get("user_id", ""),
                        "tenantId": payload.get("tenant_id", ""),
                        "accessToken": token_val,
                        "expiresAt": payload.get("exp", 0),
                        "username": "",  # JWT payload 里没有, 不影响后端鉴权
                    }
                    auth_str = json.dumps(auth_synth, ensure_ascii=False)
                    logger.info("   [DEBUG] 用 request 监听器抓到的 Bearer 合成 auth JSON")
                    break

            # 每 5 秒 reload 一次 token_page
            # 保证 SSO cookie 建立后, SPA 有机会重新拉 token 写 localStorage
            if time.time() - last_reload > RELOAD_INTERVAL:
                try:
                    token_page.goto(TOKEN_ORIGIN)
                except Exception:
                    pass
                last_reload = time.time()

            time.sleep(1)

        if not auth_str:
            ctx.close()
            raise Exception(
                f"❌ 等待登录超时({LOGIN_TIMEOUT_MS // 1000} 秒),请检查是否成功扫码"
            )

        ctx.close()

    auth_json = _parse_auth_json(auth_str)
    if not auth_json or not auth_json.get("accessToken"):
        raise Exception(f"❌ 从 localStorage 拿到的数据无效: {auth_str}")

    return auth_json


def get_dev_token():
    """
    获取小贝管理后台的 accessToken

    优先级:
    1. XIAOBEI_TOKEN 环境变量/配置 → 直接返回(不做过期检查)
    2. NORTH_NOVA_BO_AUTH 里的 accessToken → 检查 expiresAt,没过期就返回
    3. _DEFAULT_AUTH_JSON 内嵌 seed → 检查 expiresAt,没过期就用(git clone 后开箱即用)
    4. 上面都失败 → Playwright 开浏览器抓 token,并回写 .env.local
    """
    # 路径 1: 显式配置的 XIAOBEI_TOKEN(测试专用长期 token 场景)
    manual_token = get_env_value("XIAOBEI_TOKEN")
    if manual_token:
        return manual_token

    # 路径 2: 用 .env.local 里的 NORTH_NOVA_BO_AUTH(如果没过期)
    auth_text = get_env_value("NORTH_NOVA_BO_AUTH") or get_env_value("north_nova_bo_auth")
    auth_json = _parse_auth_json(auth_text)

    if _is_auth_valid(auth_json):
        exp = auth_json.get("expiresAt", 0)
        remaining_days = (exp - int(time.time())) // 86400
        logger.info(f"✅ 使用 .env.local 里的 token (剩余 {remaining_days} 天)")
        return auth_json["accessToken"]

    # 路径 3: 用本文件内嵌的 seed token(git clone 后开箱即用)
    if _is_auth_valid(_DEFAULT_AUTH_JSON):  
        exp = _DEFAULT_AUTH_JSON.get("expiresAt", 0)
        remaining_days = (exp - int(time.time())) // 86400
        logger.info(f"✅ 使用代码内嵌 seed token (剩余 {remaining_days} 天)")
        return _DEFAULT_AUTH_JSON["accessToken"]

    # 路径 4: 兜底 —— 开浏览器抓
    if auth_json:
        logger.warning("⚠️ .env.local 里的 token 已过期,启动浏览器重新获取...")
    else:
        logger.info("ℹ️ 无可用 token(.env.local 和内嵌 seed 均无效),启动浏览器获取...")

    new_auth = _fetch_token_via_browser()

    # 写回 .env.local,下次运行直接用
    new_auth_str = json.dumps(new_auth, ensure_ascii=False)
    update_env_local("NORTH_NOVA_BO_AUTH", new_auth_str)

    exp = new_auth.get("expiresAt", 0)
    if exp:
        exp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        logger.info(f"✅ 新 token 已保存到 .env.local (有效期至 {exp_str})")
    else:
        logger.info("✅ 新 token 已保存到 .env.local")

    return new_auth["accessToken"]


# ============================================
# 兼容层:保持现有 `from config.get_token import token` 的写法
# 模块首次 import 时执行一次
# ============================================
token = TOKEN = get_dev_token()
