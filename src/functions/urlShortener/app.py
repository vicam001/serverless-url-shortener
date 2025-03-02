import json
import os
import uuid
import boto3
import base64
import re
from urllib.parse import urlparse
import requests
from botocore.exceptions import BotoCoreError, ClientError

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def shorten(event, context):
    """Shorten a given URL"""
    try:
        body = json.loads(event.get('body', '{}'))  # Handle missing body
    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON format"})

    original_url = body.get("url")

    if not original_url or not is_valid_url(original_url):
        return response(400, {"error": "Invalid or missing URL"})

    short_id = generate_short_id()

    try:
        table.put_item(Item={"shortId": short_id, "originalUrl": original_url})
    except (BotoCoreError, ClientError) as e:
        return response(500, {"error": "Database error", "details": str(e)})

    # Construct the short URL dynamically based on the request context
    api_base_url = f"https://{event['headers'].get('Host', '')}/{event.get('requestContext', {}).get('stage', '')}/"
    short_url = f"{api_base_url}{short_id}"

    return response(200, {"short_url": short_url})

def redirect(event, context):
    """Redirect to the original URL"""
    short_id = event.get("pathParameters", {}).get("shortId")

    if not short_id:
        return response(400, {"error": "Short ID missing"})

    try:
        response_item = table.get_item(Key={"shortId": short_id})
    except (BotoCoreError, ClientError) as e:
        return response(500, {"error": "Database error", "details": str(e)})

    if "Item" not in response_item:
        return response(404, {"error": "Short URL not found"})

    return {
        "statusCode": 301,
        "headers": {"Location": response_item["Item"]["originalUrl"]}
    }


def forward(event, context):
    """Forwards the POST request to the original URL"""
    short_id = event.get("pathParameters", {}).get("shortId")

    if not short_id:
        return response(400, {"error": "Short ID missing"})

    try:
        response_item = table.get_item(Key={"shortId": short_id})
    except (BotoCoreError, ClientError) as e:
        return response(500, {"error": "Database error", "details": str(e)})

    if "Item" not in response_item:
        return response(404, {"error": "Short URL not found"})

    original_url = response_item["Item"]["originalUrl"]

    print(f"Forwarding request to {original_url[:40]}")

    # Extract and parse request body
    raw_data = event.get('body', '{}')

    # Parse the JSON string into a dictionary
    try:
        parsed_data = json.loads(raw_data)  # Convert to a Python dictionary
    except json.JSONDecodeError:
        print("Invalid JSON data")
        parsed_data = {}


    # Forward headers
    headers = {"Content-Type": "application/json"}

    try:
        requests.post(original_url, json=parsed_data, headers=headers, timeout=5)
    except requests.exceptions.RequestException as e:
        return response(500, {"error": "Forwarding error", "details": str(e)})
    print("Webhook forwarded successfully")
    return response(200, {"message": "Webhook forwarded successfully"})

def is_valid_url(url):
    """Basic URL validation with regex"""
    regex = re.compile(
        r"^(https?://)"  # http or https
        r"((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|"  # Domain
        r"localhost|"  # Localhost
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"  # IPv4
        r"(:\d+)?(/.*)?$"  # Optional port and path
    )
    return re.match(regex, url) is not None

def generate_short_id():
    """Generate a URL-friendly, 6-character base62 short ID"""
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:6].decode('utf-8')

def response(status_code, body):
    """Helper function to format HTTP response"""
    return {"statusCode": status_code, "body": json.dumps(body)}
