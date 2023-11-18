import json
import boto3
from hashlib import sha256
from datetime import datetime, timedelta

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Tables
visitor_counter_table = dynamodb.Table('VisitorCounter')
unique_visitor_table = dynamodb.Table('UniqueVisitors')

def hash_ip(ip_address):
    # Create a SHA-256 hash of the IP address
    return sha256(ip_address.encode('utf-8')).hexdigest()

def lambda_handler(event, context):
    # Extract the IP address from the request context provided by API Gateway
    ip_address = event['requestContext']['identity']['sourceIp']
    hashed_ip = hash_ip(ip_address)
    
    # Define the timeframe in which a visitor is counted as unique
    timeframe_limit = datetime.now() - timedelta(days=1)
    
    unique_visits = None
    
    # Try to retrieve the unique visitor from the table
    try:
        response = unique_visitor_table.get_item(Key={'hashed_ip': hashed_ip})
        item = response.get('Item')
        
        # If the visitor is new or last visited earlier than the timeframe limit
        if not item or datetime.fromisoformat(item['last_visited']) < timeframe_limit:
            # Visitor is unique within the timeframe
            unique_visitor_table.put_item(
                Item={
                    'hashed_ip': hashed_ip,
                    'last_visited': datetime.now().isoformat()
                }
            )
            # Increment the unique visitor count
            unique_response = visitor_counter_table.update_item(
                Key={'id': 'unique'},
                UpdateExpression='ADD visits :inc',
                ExpressionAttributeValues={':inc': 1},
                ReturnValues="UPDATED_NEW"
            )
            unique_visits = unique_response['Attributes']['visits']

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "Internal Server Error"})
        }
    
    # Increment the total visitor count
    total_response = visitor_counter_table.update_item(
        Key={'id': 'total'},
        UpdateExpression='ADD visits :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues="UPDATED_NEW"
    )
    
    # Prepare the response body
    body = {
        'total_visits': total_response['Attributes']['visits']
    }
    if unique_visits is not None:
        body['unique_visits'] = unique_visits
    
    # Return the updated counts
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body)
    }
