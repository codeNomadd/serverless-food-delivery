import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get("DYNAMODB_TABLE")  # Use .get() to avoid crashing on missing var
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event, indent=2))  # Debug log

        # Parse request body safely
        body = json.loads(event.get("body", "{}"))
        
        print("Parsed body:", body)  # Debug log

        if "OrderID" not in body or "CustomerName" not in body or "TotalPrice" not in body:
            raise ValueError("Missing required order fields")

        # Insert into DynamoDB
        response = table.put_item(Item={
            "orderId": body["OrderID"],
            "customerName": body["CustomerName"],
            "totalPrice": str(body["TotalPrice"]),  # Convert to string for DynamoDB
            "status": "Pending"
        })

        print("DynamoDB Response:", response)  # Debug log

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Order placed successfully!"})
        }

    except Exception as e:
        print("Error:", str(e))  # Debug log
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
