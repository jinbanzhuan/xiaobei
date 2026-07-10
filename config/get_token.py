import json
import os
import time

# ============================================
# 小贝 token 获取
# 优先级:
#   1. .env.local 里显式配的 XIAOBEI_TOKEN(直接使用,不做过期检查)
#   2. .env.local 里的 NORTH_NOVA_BO_AUTH JSON(检查 expiresAt,没过期就用)
#   3. Playwright 打开浏览器 → 飞书扫码 → 从 localStorage 抓 token → 写回 .env.local
#
# 首次使用:会弹出 Chromium 窗口让你扫码,扫完自动关闭
# 之后使用:浏览器数据被缓存到 BROWSER_DATA_DIR,大概率无需重新扫码
# ============================================

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")

# 浏览器数据持久化目录:飞书 cookie / 小贝 session 都在这里
# 一次扫码后,后续启动是"已登录"状态,不用再扫
BROWSER_DATA_DIR = os.path.expanduser("~/.xiaobei_playwright_data")

# 小贝管理后台前端地址(飞书扫码入口)
# 注意: dev-bo.xiaobei.top 对某些组织会提示"暂不支持当前组织", 用 dev.xiaobei.top 打开登录页更友好
XIAOBEI_LOGIN_URL = "https://dev.xiaobei.top"

# token 真正落在哪个 origin 的 localStorage
# 老前端 SPA (dev-bo) 加载后会调 API 拉 token 并写入自己 origin 的 localStorage
# 所以必须去这个 origin 才能读到 north_nova_bo_auth
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

    except Exception as e:
        print(f"读取.env.local失败: {e}")
        raise


def update_env_local(key, value):
    """
    更新 .env.local 里的某个 key(不存在则追加)
    Playwright 抓到新 token 后自动写回,下次跑不用重开浏览器
    """
    lines = []
    found = False
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
        if not found:
            if lines and not lines[-1].endswith("\n"):
                lines.append("\n")
            lines.append(f"{key}={value}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"⚠️ 写入 .env.local 失败(不影响本次运行): {e}")


def _parse_auth_json(auth_text):
    """安全解析 NORTH_NOVA_BO_AUTH 的 JSON 字符串"""
    if not auth_text:
        return None
    try:
        return json.loads(auth_text)
    except Exception as e:
        print(f"⚠️ 解析 NORTH_NOVA_BO_AUTH 失败: {e}")
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
        print("🌐 首次登录,即将打开 Chromium 浏览器,请用飞书扫码...")
    else:
        print("🌐 尝试用缓存的浏览器数据登录...")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,  # 始终显示窗口,以防 cookie 过期需要重新扫码
        )

        # tab 1: 用户扫码用, 打开友好的登录页
        login_page = ctx.new_page()
        login_page.goto(XIAOBEI_LOGIN_URL)

        # tab 2: 只为了能读 TOKEN_ORIGIN 的 localStorage
        # 老前端 SPA(dev-bo)加载后会自动调 API 拉 token 写进自己 origin 的 localStorage
        token_page = ctx.new_page()
        try:
            token_page.goto(TOKEN_ORIGIN)
        except Exception:
            pass  # dev-bo 首页可能显示"暂不支持当前组织", 忽略即可, 只要 localStorage 能读就行

        # 轮询 token_page.localStorage
        # 每 1 秒读一次, 每 5 秒 reload 一次 token_page 让 SPA 有机会重新拉 token
        # 用 Python 外层 while 而不是 page.wait_for_function, 因为跨 origin 跳转会
        # destroy execution context, wait_for_function 会挂死
        import time as _time
        deadline = _time.time() + LOGIN_TIMEOUT_MS / 1000
        auth_str = None
        last_login_url = ""
        last_reload = _time.time()
        RELOAD_INTERVAL = 5

        while _time.time() < deadline:
            # 打印登录 tab 的 URL 变化, 方便用户看扫码进度
            try:
                cur_url = login_page.url
                if cur_url != last_login_url:
                    print(f"🔍 登录页跳转: {cur_url}")
                    last_login_url = cur_url
            except Exception:
                pass

            # 从 token_page 读 localStorage
            try:
                auth_str = token_page.evaluate(
                    f"() => localStorage.getItem('{AUTH_STORAGE_KEY}')"
                )
                if auth_str:
                    break
            except Exception:
                # token_page 可能正在跳转 / execution context 被销毁, 忽略
                pass

            # 每 5 秒 reload 一次 token_page
            # 保证 SSO cookie 建立后, SPA 有机会重新拉 token 写 localStorage
            if _time.time() - last_reload > RELOAD_INTERVAL:
                try:
                    token_page.goto(TOKEN_ORIGIN)
                except Exception:
                    pass
                last_reload = _time.time()

            _time.sleep(1)

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
    获取 dev-bo 页面的 accessToken

    优先级:
    1. XIAOBEI_TOKEN 环境变量/配置 → 直接返回(不做过期检查)
    2. NORTH_NOVA_BO_AUTH 里的 accessToken → 检查 expiresAt,没过期就返回
    3. 上面都失败 → Playwright 开浏览器抓 token,并回写 .env.local
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
        print(f"✅ 使用 .env.local 里的 token (剩余 {remaining_days} 天)")
        return auth_json["accessToken"]

    # 路径 3: 兜底 —— 开浏览器抓
    if auth_json:
        print("⚠️ .env.local 里的 token 已过期,启动浏览器重新获取...")
    else:
        print("ℹ️ .env.local 里没有 token,启动浏览器获取...")

    new_auth = _fetch_token_via_browser()

    # 写回 .env.local,下次运行直接用
    new_auth_str = json.dumps(new_auth, ensure_ascii=False)
    update_env_local("NORTH_NOVA_BO_AUTH", new_auth_str)

    exp = new_auth.get("expiresAt", 0)
    if exp:
        exp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        print(f"✅ 新 token 已保存到 .env.local (有效期至 {exp_str})")
    else:
        print("✅ 新 token 已保存到 .env.local")

    return new_auth["accessToken"]


def get_headers():
    """获取带 token 的请求头"""
    return {
        "accept-language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_dev_token()}",
    }


# ============================================
# 兼容层:保持现有 `from config.get_token import token` 的写法
# 模块首次 import 时执行一次
# ============================================
token = get_dev_token()
TOKEN = token
