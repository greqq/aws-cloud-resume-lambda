import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VisitorCounter')

def lambda_handler(event, context):
    # Check if there's an unexpected body
    if event.get("body"):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bad Request: unexpected request body'})
        }
    
    # If there's no body, proceed with updating the counter
    response = table.update_item(
        Key={'id': 'counter'},
        UpdateExpression='ADD visits :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues="UPDATED_NEW"
    )
    
    # Return number of visits
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': str(response['Attributes']['visits'])
    }
