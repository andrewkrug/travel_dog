import boto3
from logging import getLogger
from flask.logging import default_handler
from os import getenv

log = getLogger(__name__)
log.addHandler(default_handler)


def get_session():
    return boto3.session.Session(region_name=getenv("AWS_REGION", "us-west-2"))


def get_table(session):
    dynamo_local_host = getenv("DYNAMO_LOCAL_HOST")
    dynamo_local_port = getenv("DYNAMO_LOCAL_PORT")
    dynamo_enable_local = getenv("DYNAMO_ENABLE_LOCAL", "False").lower()

    if dynamo_enable_local == "true":
        r = session.resource(
            "dynamodb", endpoint_url=f"http://{dynamo_local_host}:{dynamo_local_port}"
        )
    else:
        r = session.resource("dynamodb")
    t = r.Table("traveldog-users")

    return t


def get_dynamo_client(boto_session):
    dynamo_local_host = getenv("DYNAMO_LOCAL_HOST")
    dynamo_local_port = getenv("DYNAMO_LOCAL_PORT")
    dynamo_enable_local = getenv("DYNAMO_ENABLE_LOCAL", "False").lower()

    if dynamo_enable_local == "true":
        log.info(
            "The dynamodb client will run in local mode connected to the local db."
        )
        client = boto_session.client(
            "dynamodb", endpoint_url=f"http://{dynamo_local_host}:{dynamo_local_port}"
        )
        log.info(
            "Environment variables indicate running locally. Returning custom endpoint."
        )
    else:
        client = boto_session.client("dynamodb", region_name="us-west-2")
        log.info(
            "Environment variables indicate that we are running in AWS. Returning normal client."
        )

    return client


def list_tables(boto_session):
    client = get_dynamo_client(boto_session)
    response = client.list_tables()
    return response
