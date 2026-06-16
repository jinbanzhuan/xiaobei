import os
import requests
import pytest
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from config.get_token import TOKEN
from utils.api_client import BASE_URL


class TestApiClient:
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    enterprise_id = "7e367d34-ab10-41a6-b682-fc696bc76c63"  # 替换成真实 eid

    @pytest.mark.上传企业附件
    def test_upload_enterprise_attachment(self):
        """
        企业附件三段式上传：
        1) POST /api/v1/uploads/presign           申请预签名 URL
        2) PUT  uploadUrl                         直传 TOS
        3) POST /api/v1/policy-match/enterprises/{eid}/attachments/register
                                                  登记到企业 + 移动到业务目录
        """
        file_path = "/Users/jinyang/Desktop/test_50MB.docx"
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        content_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # 1) presign
        presign = requests.post(
            f"{BASE_URL}/api/v1/uploads/presign",
            headers=self.headers,
            json={
                "fileName": file_name,
                "contentType": content_type,
                "fileSize": file_size,
            },
            verify=False,
        )
        assert presign["code"] == 0, presign
        upload_url = presign["data"]["uploadUrl"]
        object_key = presign["data"]["objectKey"]

        # 2) PUT TOS（只带 Content-Type，不要 Authorization）
        with open(file_path, "rb") as f:
            tos_resp = requests.put(
                upload_url,
                data=f,
                headers={"Content-Type": content_type},
                verify=False,
                timeout=300,
            )
        assert tos_resp.status_code == 200, tos_resp.text

        # 3) register 到企业
        register = requests.post(
            f"{BASE_URL}/api/v1/policy-match/enterprises/{self.enterprise_id}/attachments/register",
            headers=self.headers,
            json={
                "objectKey": object_key,
                "name": file_name,
                "mimeType": content_type,
                "sizeBytes": file_size,
                "source": "api-test",
            },
            verify=False,
        ).json()
        # assert register["code"] == 0, register
        attachment = register["data"]["attachment"]
        # assert attachment["id"]
        # assert attachment["storagePath"].startswith(
        #     f"enterprises/{self.enterprise_id}/attachments/"
        # )
        print(f"\n企业附件登记成功: {attachment}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
