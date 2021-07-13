import boto3
import logging
import pyperclip
import ast
from botocore.exceptions import ClientError
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
uploads_bucket = "python-upload-target"
transcriptions_bucket = "python-transcribe-target"
def upload_file(file, bucket, object_name=None):
    if object_name==None:
        object_name=file
    try:
        response = s3.upload_file(file, uploads_bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return response

def upload_fileObject(file, bucket):
    try:
        response = s3.upload_fileobj(
            file, bucket, file.filename
        )
    except ClientError as e:
        logging.error(e)
        return False
    return response

def create_transcript(source, bucket, job_name=None):
    if job_name==None:
        job_name=source
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaFormat=source.rsplit('.', 1)[1].lower(),
            Media={
                'MediaFileUri':source
            },
            OutputBucketName=bucket
            )
    except ClientError as e:
        logging.error(e)
        return False
    return response

def create_transcript_medical(source, bucket, job_name=None):
    if job_name==None:
        job_name=source
    try:
        response = transcribe.start_medical_transcription_job(
            MedicalTranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaFormat=source.rsplit('.', 1)[1].lower(),
            Media={
                'MediaFileUri':source
            },
            OutputBucketName=bucket,
            Specialty="PRIMARYCARE",
            Type="CONVERSATION"
            )
    except ClientError as e:
        logging.error(e)
        return False
    return response

def get_file_list(s3Bucket):
    try:
        response = s3.list_objects_v2(
            Bucket=s3Bucket
        )
        itemList = []
        for item in response["Contents"]:
            itemList.append(item)
        print(itemList)
        return itemList
    except ClientError as e:
        logging.log(e)
        return False
def get_file(bucket, key):
    try:
        response = s3.get_object(
            Bucket=bucket, 
            Key=key
        )
        body = ast.literal_eval(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        logging.log(e)
        return False
    return body
# print(upload_file("us_accent_cancer.mp3", uploads_bucket))
# print(create_transcript_medical("s3://aks-learning-2021/us_accent_cancer.mp3", transcriptions_bucket, "python-transcribe-medical"))
# print(create_transcript("s3://aks-learning-2021/us_accent_cancer.mp3", transcriptions_bucket, "python-transcribe-normal"))
# response = get_file(transcriptions_bucket, "python-transcribe-normal.json")
# # print(response)
# body = ast.literal_eval(response['Body'].read().decode('utf-8'))
# print(type(body))
# for item in body['results']['items']:
#     # if item['type'] == "pronunciation":
#     #     print(item['alternatives'][0]['content'], end=" ")
#     # else:
#     #     print(item['alternatives'][0]['content'], end="")
#     print(item)
# for item in body['items']:
#     print(item)
# pyperclip.copy(str(body))