"""
生成小北 BO 后台的 auth JSON (前端 localStorage.north_nova_bo_auth 结构)

用法:
    python -m config.gen_bo_auth                    # 打印, 不改文件
    python -m config.gen_bo_auth --write            # 写回 .env.local
    python -m config.gen_bo_auth --expire 86400     # 自定义有效期(秒)

依赖 .env.local:
    XIAOBEI_JWT_SIGNING_SECRET / XIAOBEI_USER_ID /
    XIAOBEI_TENANT_ID / XIAOBEI_USERNAME(可选)
"""
import argparse
import json
import os
import time

import jwt

from config.get_xiaobei_api import get_env_value


def gen_bo_auth(expire: int = 604800):
    """从 .env.local 读取依赖, 签发 HS256 JWT, 返回 auth JSON dict"""
    secret = get_env_value("XIAOBEI_JWT_SIGNING_SECRET")
    user_id = get_env_value("XIAOBEI_USER_ID")
    tenant_id = get_env_value("XIAOBEI_TENANT_ID")
    username = get_env_value("XIAOBEI_USERNAME") or ""

    missing = [k for k, v in {
        "XIAOBEI_JWT_SIGNING_SECRET": secret,
        "XIAOBEI_USER_ID": user_id,
        "XIAOBEI_TENANT_ID": tenant_id,
    }.items() if not v]
    if missing:
        raise RuntimeError(f"缺少必填配置 {missing}, 请先在 .env.local 里补齐")

    now = int(time.time())
    exp = now + expire
    token = jwt.encode(
        {"user_id": user_id, "tenant_id": tenant_id, "iat": now, "exp": exp},
        secret,
        algorithm="HS256",
    )
    return {
        "userId": user_id,
        "tenantId": tenant_id,
        "accessToken": token,
        "expiresAt": exp,
        "username": username,
    }


def _write_env_local(key: str, value: str):
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
    lines = []
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        pass

    new_line = f"{key}={value}\n"
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = new_line
            break
    else:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(new_line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(description="生成小北 BO 后台 auth JSON")
    parser.add_argument("--expire", type=int, default=604800, help="有效期(秒), 默认 7 天")
    parser.add_argument("--write", action="store_true", help="写回 .env.local")
    args = parser.parse_args()

    auth = gen_bo_auth(expire=args.expire)
    auth_json_str = json.dumps(auth, ensure_ascii=False)
    exp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(auth["expiresAt"]))

    print(f"✅ 已生成 auth JSON (有效期至 {exp_str})")
    print(auth_json_str)

    if args.write:
        _write_env_local("NORTH_NOVA_BO_AUTH", auth_json_str)
        print("✅ 已写回 .env.local -> NORTH_NOVA_BO_AUTH")


if __name__ == "__main__":
    main()
