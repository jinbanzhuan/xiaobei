import os

from utils.logger import get_logger

logger = get_logger(__name__)

# 强制 .env.local 提供 EXP_NORTH_APP_* 配置, 缺失即 raise, 避免 secret 落进代码库

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")


def get_env_value(key):
    """读取 key: 系统环境变量 > .env.local; 读不到返回空串"""
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
        logger.error(f".env.local 不存在: {env_path}")
    except Exception as e:
        logger.error(f"读取.env.local失败: {e}")

    return ""


# 按 EXP 租户读取; 换租户改 .env.local 里的 EXP_NORTH_APP_* 值即可
north_app_base_url = get_env_value("EXP_NORTH_APP_BASE_URL")
north_app_client_id = get_env_value("EXP_NORTH_APP_CLIENT_ID")
north_app_client_secret = get_env_value("EXP_NORTH_APP_CLIENT_SECRET")
north_app_workspace_id = get_env_value("EXP_NORTH_APP_WORKSPACE_ID")
north_app_agent_user_id = get_env_value("EXP_NORTH_APP_AGENT_USER_ID")

_missing = [k for k, v in {
    "EXP_NORTH_APP_BASE_URL": north_app_base_url,
    "EXP_NORTH_APP_CLIENT_ID": north_app_client_id,
    "EXP_NORTH_APP_CLIENT_SECRET": north_app_client_secret,
    "EXP_NORTH_APP_WORKSPACE_ID": north_app_workspace_id,
    "EXP_NORTH_APP_AGENT_USER_ID": north_app_agent_user_id,
}.items() if not v]
if _missing:
    raise RuntimeError(f"缺少必填配置 {_missing}, 请在 .env.local 里补齐")
