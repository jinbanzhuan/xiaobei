#!/usr/bin/env python3
import requests
import json
import sys
import os


def send_feishu_message(webhook_url, status, job_name, build_number, build_url, report_url):
    """
    发送飞书消息
    """
    if status == "SUCCESS":
        title = "✅ 自动化测试通过"
        color = "green"
        status_text = "通过 ✅"
    else:
        title = "❌ 自动化测试失败"
        color = "red"
        status_text = "失败 ❌"

    # 构建飞书富文本消息
    content = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {"tag": "text", "text": f"📋 项目：{job_name}"}
                        ],
                        [
                            {"tag": "text", "text": f"🔢 构建编号：#{build_number}"}
                        ],
                        [
                            {"tag": "text", "text": f"📊 状态：{status_text}"}
                        ],
                        [
                            {"tag": "a", "text": "📈 查看 Allure 报告", "href": report_url}
                        ],
                        [
                            {"tag": "a", "text": "📝 查看控制台日志", "href": f"{build_url}console"}
                        ],
                        [
                            {"tag": "text", "text": f"🕐 时间：{os.popen('date').read().strip()}"}
                        ]
                    ]
                }
            }
        }
    }

    # 发送请求
    try:
        response = requests.post(webhook_url, json=content, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            print("✅ 飞书消息发送成功")
        else:
            print(f"❌ 飞书消息发送失败：{result}")
    except Exception as e:
        print(f"❌ 发送异常：{e}")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("参数不足")
        print("用法: python send_feishu.py <webhook_url> <status> <job_name> <build_number> <build_url> <report_url>")
        sys.exit(1)

    webhook_url = sys.argv[1]
    status = sys.argv[2]
    job_name = sys.argv[3]
    build_number = sys.argv[4]
    build_url = sys.argv[5]
    report_url = sys.argv[6]

    send_feishu_message(webhook_url, status, job_name, build_number, build_url, report_url)