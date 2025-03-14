import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get("DYNAMODB_TABLE", "FoodOrders")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Handles HTTP requests for Order Management.
    Supports POST (create), GET (fetch), PUT (update), and DELETE (cancel).
    """
    try:
        print("Received event:", json.dumps(event, indent=2))

        http_method = event["httpMethod"]

        if http_method == "POST":
            return create_order(event)
        elif http_method == "GET":
            return get_order(event)
        elif http_method == "PUT":
            return update_order(event)
        elif http_method == "DELETE":
            return delete_order(event)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unsupported HTTP method"})}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# ✅ 1. CREATE ORDER (POST)
def create_order(event):
    """
    Stores a new order in DynamoDB.
    """
    body = json.loads(event.get("body", "{}"))

    if "CustomerName" not in body or "TotalPrice" not in body or "Items" not in body:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields"})}

    order_id = str(uuid.uuid4())
    timestamp = str(datetime.utcnow())

    order = {
        "orderId": order_id,
        "customerName": body["CustomerName"],
        "items": body["Items"],  # Expecting a list of food items
        "totalPrice": str(body["TotalPrice"]),
        "status": "Pending",
        "createdAt": timestamp
    }

    table.put_item(Item=order)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Order placed successfully!", "orderId": order_id})
    }

# ✅ 2. FETCH ORDER (GET)
def get_order(event):
    """
    Retrieves an order by orderId.
    """
    order_id = event.get("queryStringParameters", {}).get("orderId")

    if not order_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing orderId"})}

    response = table.get_item(Key={"orderId": order_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Order not found"})}

    # Ensure proper JSON response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response["Item"], indent=2)  # Pretty-print JSON
    }


# ✅ 3. UPDATE ORDER STATUS (PUT)
def update_order(event):
    """
    Updates order status (e.g., Pending → Delivered).
    """
    body = json.loads(event.get("body", "{}"))

    if "orderId" not in body or "status" not in body:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing orderId or status"})}

    order_id = body["orderId"]
    new_status = body["status"]

    response = table.update_item(
        Key={"orderId": order_id},
        UpdateExpression="SET #s = :new_status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":new_status": new_status},
        ReturnValues="UPDATED_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Order updated successfully!", "updatedFields": response["Attributes"]})
    }

# ✅ 4. DELETE ORDER (DELETE)
def delete_order(event):
    """
    Cancels an order.
    """
    body = json.loads(event.get("body", "{}"))

    if "orderId" not in body:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing orderId"})}

    order_id = body["orderId"]

    response = table.delete_item(Key={"orderId": order_id})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Order cancelled successfully!"})
    }
