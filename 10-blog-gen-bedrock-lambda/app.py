import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    prompt = f'''
<s>
[INST] Generate a 200 words blog post about {blogtopic} Assistant  [/INST]
'''
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.7
    }

    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,
                retries={"max_attempts": 3, "mode": "standard"}
            )
        )

        bedrock_response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0"
        )

    
        response_content = bedrock_response["body"].read().decode("utf-8")
        response_data = json.loads(response_content)
        print("Bedrock response:", response_data)

        
        blog_details = response_data['generation']
        return blog_details

    except Exception as e:
        print(f"Error occurred: {e}")  
        return None

def save_blog_to_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client("s3")
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print(f"Blog post saved to s3://{s3_bucket}/{s3_key}")
        return True
    except Exception as e:
        print(f"Error saving blog post to S3: {e}")
        return False

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        blogtopic = body.get('blogtopic')
        if not blogtopic:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'blogtopic' in request body"})
            }

        generate_blog = blog_generate_using_bedrock(blogtopic)

        if generate_blog:
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'awsbedrockgeneration'
            save_blog_to_s3(s3_key, s3_bucket, generate_blog)
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Blog generation failed"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Blog post generated and saved successfully.",
                "blog_content": generate_blog,
                "s3_path": f"s3://{s3_bucket}/{s3_key}"
            })
        }

    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
