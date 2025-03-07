import json
import boto3
import os

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Ensure the correct environment variable is being used
table_name = os.environ.get("DYNAMODB_TABLE", "FoodOrders")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Parse the incoming event
        body = json.loads(event['body'])  # Ensure event['body'] exists

        # Insert order into DynamoDB
        table.put_item(Item={
            'orderId': body['OrderID'],
            'customerName': body['CustomerName'],
            'totalPrice': str(body['TotalPrice']),  # Ensure it's stored as a string
            'status': 'Pending'
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Order placed successfully!"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
