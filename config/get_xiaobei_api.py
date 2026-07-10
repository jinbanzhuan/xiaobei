import os

# .env.local 在 xiaobei 目录下
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")


def get_env_value(key):
    """
    从 .env.local 里读取指定配置
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


# 小北原生 open API 配置，从 .env.local 读取
# 当前按 EXP 租户读取；如果要切 dev/chj，把 EXP 改成 DEV/CHJ 即可
north_app_base_url = get_env_value("EXP_NORTH_APP_BASE_URL")
north_app_client_id = get_env_value("EXP_NORTH_APP_CLIENT_ID")
north_app_client_secret = get_env_value("EXP_NORTH_APP_CLIENT_SECRET")
north_app_workspace_id = get_env_value("EXP_NORTH_APP_WORKSPACE_ID")
north_app_agent_user_id = get_env_value("EXP_NORTH_APP_AGENT_USER_ID")

if north_app_base_url == "" or north_app_client_id == "" or north_app_client_secret == "":
    raise Exception("请检查 .env.local 是否配置 EXP_NORTH_APP_BASE_URL / EXP_NORTH_APP_CLIENT_ID / EXP_NORTH_APP_CLIENT_SECRET")
