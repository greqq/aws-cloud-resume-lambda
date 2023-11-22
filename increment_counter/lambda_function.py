import json
import boto3
from hashlib import sha256
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")
visitor_counter_table = dynamodb.Table("VisitorCounter")
unique_visitor_table = dynamodb.Table("UniqueVisitors")


def hash_ip(ip_address):
    # Create a SHA-256 hash of the IP address
    return sha256(ip_address.encode("utf-8")).hexdigest()


def lambda_handler(event, context):
    ip_address = event["requestContext"]["identity"]["sourceIp"]
    hashed_ip = hash_ip(ip_address)
    timeframe_limit = datetime.now() - timedelta(days=1)

    try:
        response = unique_visitor_table.get_item(Key={"hashed_ip": hashed_ip})
        item = response.get("Item")

        # If the visitor is new or last visited earlier than the timeframe limit
        if not item or datetime.fromisoformat(item["last_visited"]) < timeframe_limit:
            # Update the 'last_visited' timestamp for the visitor
            unique_visitor_table.put_item(
                Item={
                    "hashed_ip": hashed_ip,
                    "last_visited": datetime.now().isoformat(),
                }
            )
            visitor_counter_table.update_item(
                Key={"id": "counter"},
                UpdateExpression="ADD visits :inc",
                ExpressionAttributeValues={":inc": 1},
                ReturnValues="UPDATED_NEW",
            )
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"}),
        }
    # Get the current unique visitor count
    count_response = visitor_counter_table.get_item(Key={"id": "counter"})
    unique_visits = count_response.get("Item", {}).get("visits", 0)
    unique_visits_int = int(unique_visits) if unique_visits else 0

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "https://webflowprojects.cc",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        },
        "body": json.dumps({"unique_visits": unique_visits_int}),
    }
