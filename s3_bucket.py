import constants
import boto3
import botocore
from common_utils import getS3FilePath

BUCKET_NAME_S3 = constants.S3_BUCKET_NAME

s3 = boto3.client(
    "s3",
    aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY
)


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    filePath = "user_key/" + file.filename

    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            filePath,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(bucket_name, file.filename)


def GET_S3_FILE(file_url):
    filePathValidation = getS3FilePath(file_url)

    obj = s3.get_object(Bucket=BUCKET_NAME_S3, Key=filePathValidation)

    return obj['Body'].read()
