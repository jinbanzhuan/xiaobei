import os
import time

from utils.logger import get_logger

logger = get_logger(__name__)

# token 获取优先级:
#   1. XIAOBEI_TOKEN (长期 token, 不做过期检查)
#   2. HS256 秘钥内存签发 (每次跑测试都新签一个, 不落盘)
# 想落盘 auth JSON (比如塞前端 localStorage), 手动跑 `python -m config.gen_bo_auth --write`

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
        return ""
    except FileNotFoundError:
        return ""
    except Exception as e:
        logger.error(f"读取.env.local失败: {e}")
        return ""


def get_dev_token():
    manual_token = get_env_value("XIAOBEI_TOKEN")
    if manual_token:
        return manual_token

    # 延迟 import 避免循环依赖
    from config.gen_bo_auth import gen_bo_auth
    try:
        auth = gen_bo_auth()
    except Exception as e:
        raise RuntimeError(
            f"❌ 内存签发失败: {e}\n"
            f"   请在 .env.local 配置 XIAOBEI_JWT_SIGNING_SECRET / "
            f"XIAOBEI_USER_ID / XIAOBEI_TENANT_ID"
        )
    exp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(auth["expiresAt"]))
    logger.info(f"✅ 内存签发 token (至 {exp_str})")
    return auth["accessToken"]


# 兼容 `from config.get_token import token` 的旧写法
token = TOKEN = get_dev_token()
