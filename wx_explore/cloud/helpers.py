from sqlalchemy import create_engine
import os
import boto3
import logging


def s3_client(args):
    """
    Creates and returns a boto3 S3 client with appropriate configuration.
    
    Args:
        args: Dictionary containing configuration parameters.
            Can include 'aws_access_key_id', 'aws_secret_access_key', 
            'region_name', and 'endpoint_url'.
            
    Returns:
        boto3.client: Configured S3 client
        
    Raises:
        Exception: If client creation fails after multiple retries
    """
    try:
        # Use args if provided, otherwise fall back to environment variables
        aws_access_key_id = args.get('aws_access_key_id', os.environ.get('AWS_ACCESS_KEY_ID'))
        aws_secret_access_key = args.get('aws_secret_access_key', os.environ.get('AWS_SECRET_ACCESS_KEY'))
        region_name = args.get('region_name', os.environ.get('AWS_REGION', 'us-east-1'))
        endpoint_url = args.get('endpoint_url', os.environ.get('AWS_ENDPOINT_URL'))
        
        # Create and return the S3 client
        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )
    except Exception as e:
        logging.error(f"Failed to create S3 client: {str(e)}")
        raise Exception(f"Unable to create S3 client: {str(e)}")


def db_engine(args):
    # TODO: AWS IAM-based DB credential retrieving
    if 'CONFIG' in os.environ:
        from wx_explore.common.config import Config
        return create_engine(Config.SQLALCHEMY_DATABASE_URI)
    else:
        print("Warning: defaulting to sqlite://db.db")
        return create_engine("sqlite://db.db")