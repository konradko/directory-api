import boto3


def upload_file_object_to_s3(file_object, bucket, key):
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=file_object.getvalue()
    )


def get_file_from_s3(bucket, key):
    s3 = boto3.client('s3',)
    file_object = s3.get_object(
        Bucket=bucket,
        Key=key
    )
    return file_object