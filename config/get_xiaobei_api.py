import os

# ============================================
# 小北原生 open API 配置
# 优先级: 环境变量 > .env.local > 本文件内嵌默认值(EXP 租户)
# 内嵌默认值保证 git clone 后无 .env.local 也能跑
# 如果要切 dev/chj 租户, 在 .env.local 里覆盖对应 EXP_NORTH_APP_* 即可
# ============================================

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")

# ------- 内嵌默认值 (EXP 租户 seed) -------
_DEFAULTS = {
    "EXP_NORTH_APP_BASE_URL": "https://dev-open.xiaobei.top/api/v1",
    "EXP_NORTH_APP_CLIENT_ID": "fpcli_3BhiN9SlmSi09TN7IgIow2dVGQI",
    "EXP_NORTH_APP_CLIENT_SECRET": "cNyqZsGnMc3RHOGQX~Ym-0eM3k",
    "EXP_NORTH_APP_WORKSPACE_ID": "1494a256-3b51-4711-ab00-5f9833184db0",
    "EXP_NORTH_APP_AGENT_USER_ID": "6e11917a-931c-4b41-bb60-3f82a1cbbcf7",
}


def get_env_value(key):
    """
    读取指定配置
    优先级: 系统环境变量 > .env.local 文件 > 本文件 _DEFAULTS
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
    except FileNotFoundError:
        # 没有 .env.local 是正常场景, 走内嵌默认值
        pass
    except Exception as e:
        print(f"读取.env.local失败: {e}")

    return _DEFAULTS.get(key, "")


# 小北原生 open API 配置
# 当前按 EXP 租户读取；如果要切 dev/chj，在 .env.local 里配置对应 EXP_NORTH_APP_* 覆盖即可
north_app_base_url = get_env_value("EXP_NORTH_APP_BASE_URL")
north_app_client_id = get_env_value("EXP_NORTH_APP_CLIENT_ID")
north_app_client_secret = get_env_value("EXP_NORTH_APP_CLIENT_SECRET")
north_app_workspace_id = get_env_value("EXP_NORTH_APP_WORKSPACE_ID")
north_app_agent_user_id = get_env_value("EXP_NORTH_APP_AGENT_USER_ID")

if north_app_base_url == "" or north_app_client_id == "" or north_app_client_secret == "":
    raise Exception(
        "缺少 EXP_NORTH_APP_BASE_URL / EXP_NORTH_APP_CLIENT_ID / EXP_NORTH_APP_CLIENT_SECRET, "
        "请检查 config/get_xiaobei_api.py 内嵌默认值或 .env.local 配置"
    )
