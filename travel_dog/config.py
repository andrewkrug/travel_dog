import os
import boto3


def get_ld_api_key():
    LD_API_KEY = os.getenv("LD_API_KEY")

    if LD_API_KEY != None:
        return LD_API_KEY
    else:
        client = boto3.client("ssm")
        resp = client.get_parameter(
            Name="/datadog/reinvent2022/ld_api_key", WithDecryption=True
        )
        return resp["Parameter"]["Value"]


BASE_URL = os.getenv("BASE_URL", "http://localhost")
CREATE_TABLES = os.getenv("CREATE_TABLES", "True")
