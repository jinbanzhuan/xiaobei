#!/usr/bin/env python3
import requests
import json
import sys

def send_feishu_message(webhook_url, status, job_name, build_number, build_url, report_url):
    if status == "SUCCESS":
        title = "✅ API自动化测试通过"
        status_text = "通过 ✅"
    else:
        title = "❌ API自动化测试失败"
        status_text = "失败 ❌"

    content = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{"tag": "text", "text": f"📋 项目:{job_name}"}],
                        [{"tag": "text", "text": f"🔢 构建编号:#{build_number}"}],
                        [{"tag": "text", "text": f"📊 状态:{status_text}"}],
                        [{"tag": "a", "text": "📈 查看 Allure 报告", "href": report_url}],
                        [{"tag": "a", "text": "📝 查看控制台日志", "href": f"{build_url}console"}]
                    ]
                }
            }
        }
    }

    try:
        response = requests.post(webhook_url, json=content, timeout=10)
        result = response.json()
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {result}")
        if result.get("code") == 0:
            print("✅ 飞书消息发送成功")
        else:
            print(f"❌ 飞书消息发送失败：{result}")
    except Exception as e:
        print(f"❌ 发送异常：{e}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("参数不足: webhook_url status job_name build_number build_url report_url")
        sys.exit(1)
    send_feishu_message(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
