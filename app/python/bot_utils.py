import boto3
from botocore import exceptions as boto_exceptions
from loguru import logger
from collections import Counter
import os
import json
from boto3.dynamodb.types import TypeDeserializer

aws_profile = os.getenv("AWS_PROFILE", None)
if aws_profile is not None and aws_profile == "dev":
    boto3.setup_default_session(profile_name=aws_profile)

TABLE_NAME = os.environ['TABLE_NAME']

def get_secret_value(region_name, secret_name, key_name=None):
    try:
        secret_manager = boto3.client('secretsmanager', region_name)
    except boto_exceptions.ProfileNotFound as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A ProfileNotFound has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A ProfileNotFound has occurred.", 500
    except boto_exceptions.EndpointConnectionError as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. An EndpointConnectionError has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. An EndpointConnectionError has occurred.", 500
    except boto_exceptions.NoCredentialsError as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A NoCredentialsError has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A NoCredentialsError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A ClientError has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        response = secret_manager.get_secret_value(SecretId=secret_name)
    except secret_manager.exceptions.DecryptionFailure as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A DecryptionFailure has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A DecryptionFailure has occurred.", 400
    except secret_manager.exceptions.InternalServiceError as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A InternalServiceError has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A InternalServiceError has occurred.", 500
    except secret_manager.exceptions.InvalidParameterException as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A InvalidParameterException has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A InvalidParameterException has occurred.", 400
    except secret_manager.exceptions.InvalidRequestException as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A InvalidRequestException has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A InvalidRequestException has occurred.", 400
    except secret_manager.exceptions.ResourceNotFoundException as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A ResourceNotFoundException has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A ResourceNotFoundException has occurred.", 400
    except boto_exceptions.ClientError as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. A ClientError has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Retrieval of secret {secret_name} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Retrieval of secret {secret_name} failed. An Unknown {type(e).__name__} has occurred.", 500

    secret_str = response.get("SecretString", "")
    if not secret_str:
        logger.exception(f"Retrieval of secret {secret_name} failed. Secret value is empty")
        return f"Retrieval of secret {secret_name} failed. Secret value is empty", 500

    if key_name:
        # Parse the JSON string to get the actual values
        secret_dict = json.loads(secret_str)

        # Access the specific value you need
        secret_value = secret_dict[key_name]
    else:
        secret_value = secret_str

    logger.info(f"Fetching secret: {secret_name}, succeeded.")
    return secret_value, 200

def upload_image_to_s3(bucket_name, key, image_path):
    try:
        s3_client = boto3.client('s3')
    except boto_exceptions.ProfileNotFound as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A ProfileNotFound has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A ProfileNotFound has occurred.", 500
    except boto_exceptions.EndpointConnectionError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. An EndpointConnectionError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. An EndpointConnectionError has occurred.", 500
    except boto_exceptions.NoCredentialsError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A NoCredentialsError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A NoCredentialsError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A ClientError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        with open(image_path, 'rb') as img:
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=img)
    except FileNotFoundError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A FileNotFoundError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A FileNotFoundError has occurred.", 500
    except PermissionError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A PermissionError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A PermissionError has occurred.", 500
    except IsADirectoryError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. An IsADirectoryError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. An IsADirectoryError has occurred.", 500
    except OSError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. An {type(e).__name__} has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. An {type(e).__name__} has occurred.", 500
    except boto_exceptions.ParamValidationError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A ParamValidationError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A ParamValidationError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. A ClientError has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Upload to {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Upload to {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.", 500

    logger.info(f"Upload to {bucket_name}/{key} succeeded.")
    return f"Upload to {bucket_name}/{key} succeeded.", 200

def download_image_from_s3(bucket_name, key, image_path, images_prefix):
    if not os.path.exists(images_prefix):
        os.makedirs(images_prefix)

    try:
        s3_client = boto3.client('s3')
    except boto_exceptions.ProfileNotFound as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. A ProfileNotFound has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. A ProfileNotFound has occurred.", 500
    except boto_exceptions.EndpointConnectionError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An EndpointConnectionError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An EndpointConnectionError has occurred.", 500
    except boto_exceptions.NoCredentialsError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. A NoCredentialsError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. A NoCredentialsError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. A ClientError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
    except boto_exceptions.ClientError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. A ClientError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        with open(image_path, 'wb') as img:
            img.write(response['Body'].read())
    except PermissionError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. A PermissionError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. A PermissionError has occurred.", 500
    except IsADirectoryError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An IsADirectoryError has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An IsADirectoryError has occurred.", 500
    except OSError as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An {type(e).__name__} has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An {type(e).__name__} has occurred.", 500
    except Exception as e:
        logger.exception(f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Download from {bucket_name}/{key} failed. An Unknown {type(e).__name__} has occurred.", 500

    logger.info(f"Download from {bucket_name}/{key} to {image_path} succeeded.")
    return f"Download from {bucket_name}/{key} to {image_path} succeeded.", 200

def dynamodb_to_dict(item):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}

def get_from_db(prediction_id):
    try:
        dynamodb_client = boto3.client('dynamodb')
    except boto_exceptions.ProfileNotFound as e:
        logger.exception(f"Reading from dynamodb failed. A ProfileNotFound has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A ProfileNotFound has occurred.", 500
    except boto_exceptions.EndpointConnectionError as e:
        logger.exception(f"Reading from dynamodb failed. An EndpointConnectionError has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. An EndpointConnectionError has occurred.", 500
    except boto_exceptions.NoCredentialsError as e:
        logger.exception(f"Reading from dynamodb failed. A NoCredentialsError has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A NoCredentialsError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Reading from dynamodb failed. A ClientError has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Reading from dynamodb failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        response = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={
                'predictionId': {'S': prediction_id}
            }
        )
    except dynamodb_client.exceptions.ProvisionedThroughputExceededException as e:
        logger.exception(f"Reading from dynamodb failed. A ProvisionedThroughputExceededException has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A ProvisionedThroughputExceededException has occurred.", 500
    except dynamodb_client.exceptions.ResourceNotFoundException as e:
        logger.exception(f"Reading from dynamodb failed. A ResourceNotFoundException has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A ResourceNotFoundException has occurred.", 500
    except dynamodb_client.exceptions.RequestLimitExceeded as e:
        logger.exception(f"Reading from dynamodb failed. A RequestLimitExceeded has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A RequestLimitExceeded has occurred.", 500
    except dynamodb_client.exceptions.InternalServerError as e:
        logger.exception(f"Reading from dynamodb failed. An InternalServerError has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. An InternalServerError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Reading from dynamodb failed. A ClientError has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Reading from dynamodb failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Reading from dynamodb failed. An Unknown {type(e).__name__} has occurred.", 500

    if 'Item' in response:
        item = response['Item']
        deserialized_item = dynamodb_to_dict(item)
        logger.info(f"Successfully retrieved item: {item}")
        return deserialized_item, 200
    else:
        logger.info(f"No item found with prediction_id: {prediction_id}")
        return f"No item found with prediction_id: {prediction_id}", 404

def send_to_sqs(queue_name, message_body):
    try:
        sqs_client = boto3.client('sqs')
    except boto_exceptions.ProfileNotFound as e:
        logger.exception(f"Sending message to SQS failed. A ProfileNotFound has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. A ProfileNotFound has occurred.", 500
    except boto_exceptions.EndpointConnectionError as e:
        logger.exception(f"Sending message to SQS failed. An EndpointConnectionError has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. An EndpointConnectionError has occurred.", 500
    except boto_exceptions.NoCredentialsError as e:
        logger.exception(f"Sending message to SQS failed. A NoCredentialsError has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. A NoCredentialsError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Sending message to SQS failed. A ClientError has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Sending message to SQS failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. An Unknown {type(e).__name__} has occurred.", 500

    try:
        response = sqs_client.send_message(
            QueueUrl=queue_name,
            MessageBody=message_body
        )
    except boto_exceptions.ParamValidationError as e:
        logger.exception(f"Sending message to SQS failed. A ParamValidationError has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. A ParamValidationError has occurred.", 500
    except boto_exceptions.ClientError as e:
        logger.exception(f"Sending message to SQS failed. A ClientError has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. A ClientError has occurred.", 500
    except Exception as e:
        logger.exception(f"Sending message to SQS failed. An Unknown {type(e).__name__} has occurred.\n{str(e)}")
        return f"Sending message to SQS failed. An Unknown {type(e).__name__} has occurred.", 500

    logger.info(f"Message sent successfully. Message ID: {response['MessageId']}")
    return f"Message sent successfully. Message ID: {response['MessageId']}", 200

def parse_result(data) -> str:
    # Extract the labels
    labels = data["labels"]

    # Create a list of class values from the labels
    class_names = [label["class"] for label in labels if "class" in label]

    # Count the occurrences of each class
    class_counts = Counter(class_names)

    # Create a single text result
    return_text = "Detected Objects:\n"
    for class_name, count in class_counts.items():
        return_text += f"{class_name.capitalize()}: {count}\n"

    logger.info("Successfully parsed the results.")
    return return_text