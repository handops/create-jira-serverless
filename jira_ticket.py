import json
import requests
from requests.auth import HTTPBasicAuth
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    secret_client = boto3.client("secretsmanager")
    secret_name = "lambda/jira_ticket_creation"
    secret_response = secret_client.get_secret_value(SecretId=secret_name).get(
        "SecretString"
    )
    secret_list = json.loads(secret_response)

    url_part = secret_list.get("url_part")
    api_token = secret_list.get("api_key")
    email_id = secret_list.get("email_id")

    url = f"https://{url_part}.atlassian.net/rest/api/3/issue"
    
    auth = HTTPBasicAuth(email_id, api_token)

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        webhook = json.loads(event["body"])
        response = None
        if webhook["comment"]["body"] == "/jira":
            payload = json.dumps(
                {
                    "fields": {
                        "description": {
                            "content": [
                                {
                                    "content": [
                                        {
                                            "text": webhook["issue"]["body"],
                                            "type": "text",
                                        }
                                    ],
                                    "type": "paragraph",
                                }
                            ],
                            "type": "doc",
                            "version": 1,
                        },
                        "project": {"key": "SCRUM"},
                        "issuetype": {"id": "10003"},
                        "summary": webhook["issue"]["title"],
                    },
                    "update": {},
                }
            )

            response = requests.post(url, data=payload, headers=headers, auth=auth)
            # Return the proper response format for API Gateway
            return {
                "statusCode": response.status_code,
                "body": json.dumps(response.json()),
                "headers": {"Content-Type": "application/json"},
            }
        else:
            print("Jira issue will be created if comment include /jira")

    except Exception as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Return a 500 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # Return a 500 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # Return a 400 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # Return a 400 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # Return a 400 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "UnauthorizedException":
            # Return a 401 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        elif e.response["Error"]["Code"] == "ValidationException":
            # Return a 400 error with the exception message
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
