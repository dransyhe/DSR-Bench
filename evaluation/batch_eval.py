import openai
import anthropic
import instructor 
from instructor.cli.batch import create_from_file 
from instructor.process_response import handle_response_model
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
import vertexai 
from vertexai.batch_prediction import BatchPredictionJob
from google.cloud import storage 
import os
import sys 
import numpy as np
import time
import json
from datetime import datetime, timedelta, timezone
from tiktoken import encoding_for_model, get_encoding
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from openai.lib._pydantic import to_strict_json_schema
from evaluation.eval import extract_json


def get_batch_results(Q, args, response_format):
    if "gpt" in args.model or "o1" in args.model or "o3" in args.model or "o4" in args.model:
        client = openai.OpenAI(
            api_key = os.getenv("OPENAI_API_KEY")
        )
        filename = openai_write_query(client, Q, args, response_format)
        response = openai_upload_batch(client, filename, args)
        answers = openai_get_results(client, response, args) 
    elif "claude" in args.model:
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        request_id = claude_write_query(client, Q, args, response_format)
        answers = claude_get_results(client, request_id, args)
    elif "gemini" in args.model:
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        bucket_id = os.getenv("GOOGLE_BUCKET_ID")
        answers = gemini_batch_job(project_id, bucket_id, Q, args, response_format)

    return answers


def gemini_batch_job(project_id, bucket_id, Q, args, response_format):
    # Initialize vertexai
    vertexai.init(project=project_id, location="us-central1")

    # Upload input file to Google Cloud Storage
    input_directory = f"batch/input/{args.type}/{args.operation}"
    output_directory = f"batch/output/{args.type}/{args.operation}"
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    input_filename = os.path.join(input_directory, f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_input.jsonl")
    output_filename = os.path.join(output_directory, f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_output.jsonl")
    gcloud_input_filename = f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_input.jsonl"
    gcloud_output_filename = f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_output"
    
    # Remove $defs and $ref from the response schema recursively 
    def flatten_schema(schema: dict) -> dict:
        """Recursively inline all `$defs` and remove references."""
        if "$defs" in schema:
            definitions = schema.pop("$defs")
            def replace_refs(obj):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref_key = obj["$ref"].split("/")[-1]
                        return definitions.get(ref_key, obj)  # Inline the definition
                    return {k: replace_refs(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [replace_refs(item) for item in obj]
                return obj
            schema = replace_refs(schema)
        return schema

    response_schema = flatten_schema(response_format.model_json_schema(by_alias=True))

    with open(input_filename, "w") as f:
        for i, text in enumerate(Q):
            record = {
                "request":{
                    "contents": [
                        {"role": "user", "parts": [{"text": text}]},
                    ],
                    "systemInstruction": {
                        "role": "system",
                        "parts": [{"text": "You are a helpful assistant."}]
                    },
                    "generationConfig": {
                        'responseMimeType': 'application/json',
                        'responseSchema': response_schema 
                    }
                }
            }
            f.write(json.dumps(record) + "\n")

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_id)
    
    blob = bucket.blob(gcloud_input_filename)
    blob.upload_from_filename(input_filename)

    input_uri = f"gs://{bucket_id}/{gcloud_input_filename}"
    output_uri = f"gs://{bucket_id}/{gcloud_output_filename}"

    # Submit a batch prediction job with Gemini model
    batch_prediction_job = BatchPredictionJob.submit(
        source_model=str(args.model),
        input_dataset=input_uri,
        output_uri_prefix=output_uri,
    )

    # Check job status
    print(f"Job resource name: {batch_prediction_job.resource_name}")
    print(f"Model resource name with the job: {batch_prediction_job.model_name}")
    print(f"Job state: {batch_prediction_job.state.name}")

    # Refresh the job until complete
    while not batch_prediction_job.has_ended:
        time.sleep(5)
        batch_prediction_job.refresh()

    # Check if the job succeeds
    if batch_prediction_job.has_succeeded:
        print("Job succeeded!")
    else:
        print(f"Job failed: {batch_prediction_job.error}")

    # Check the location of the output
    print(f"Job output location: {batch_prediction_job.output_location}")

    # Download the output file
    output_location = batch_prediction_job.output_location 
    output_location = output_location[output_location.find(bucket_id)+len(bucket_id)+1:]
    output_location = output_location + "/predictions.jsonl"
    blob = bucket.blob(output_location)
    blob.download_to_filename(output_filename)

    # Process the output file
    answers = [] 
    with open(output_filename, "r") as f_jsonl:
        for line in f_jsonl:
            data = json.loads(line)
            answer = data["response"]["candidates"][0]["content"]["parts"][0]["text"]
            answers.append(answer) 
            
    return answers


def claude_write_query(client, Q, args, response_format):
    """
    Write query Q too jsonl file f_jsonl. 
    """
    inputs = Q
    requests = [] 
    _, kwargs = handle_response_model(
            response_model=response_format, mode=instructor.Mode.ANTHROPIC_JSON
        )
    for i, text in enumerate(inputs):
        request = Request(
            custom_id=str(args.type) + '_' + str(args.operation) + '_' + str(args.mode) + '_' + str(args.model) + '_' + str(args.prompt) + '_' + str(i),
            params=MessageCreateParamsNonStreaming(
                model=str(args.model),
                max_tokens=int(args.token),
                temperature=float(args.T),
                system=kwargs["system"],
                messages=[
                    {"role": "user", "content": text},
                ],
            )
        )
        requests.append(request)
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def claude_get_results(client, request_id, args):
    while True:
        response = client.messages.batches.retrieve(request_id)
        if response.processing_status == "ended":
            break
        time.sleep(600)  # Wait before polling again
    answers = [] 
    for result in client.messages.batches.results(request_id):
        match result.result.type:
            case "succeeded":
                answer = result.result.message.content[0].text
                answer = answer[answer.index("{"):]
                answer = extract_json(answer)
                answers.append(answer)
            case "errored":
                if result.result.error.type == "invalid_request":
                    # Request body must be fixed before re-sending request
                    print(f"Validation error {result.custom_id}")
                else:
                    # Request can be retried directly
                    print(f"Server error {result.custom_id}")
            case "expired":
                print(f"Request expired {result.custom_id}")
    return answers


def openai_write_query(client, Q, args, response_format):
    """
    Write query Q too jsonl file f_jsonl. 
    """
    inputs = Q

    directory = f"batch/input/{args.type}/{args.operation}"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_input.jsonl")

    if "o3" in args.model or "o4" in args.model:
        with open(filename, "w") as f_jsonl: 
            for i, text in enumerate(inputs):
                query_to_write = {
                    "custom_id": str(args.type) + '_' + str(args.operation) + '_' + str(args.mode) + '_' + str(args.model) + '_' + str(args.prompt) + '_' + str(i),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": str(args.model),
                        "messages": [
                            {"role": "developer", "content": "You are a helpful assistant."},
                            {"role": "user", "content": text},
                        ],
                        "max_completion_tokens": int(args.token),
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "output_format", 
                                "schema": to_strict_json_schema(response_format), # response_format.model_json_schema(),
                                "strict": True 
                            }
                        },
                    }
                }
                if i != len(inputs) - 1:
                    f_jsonl.write(json.dumps(query_to_write) + "\n")
                else:
                    f_jsonl.write(json.dumps(query_to_write))
    else:
        with open(filename, "w") as f_jsonl: 
            for i, text in enumerate(inputs):
                query_to_write = {
                    "custom_id": str(args.type) + '_' + str(args.operation) + '_' + str(args.mode) + '_' + str(args.model) + '_' + str(args.prompt) + '_' + str(i),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": str(args.model),
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": text},
                        ],
                        "temperature": float(args.T),
                        "max_tokens": int(args.token),
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "output_format", 
                                "schema": to_strict_json_schema(response_format), # response_format.model_json_schema(),
                                "strict": True 
                            }
                        },
                    }
                }
                if i != len(inputs) - 1:
                    f_jsonl.write(json.dumps(query_to_write) + "\n")
                else:
                    f_jsonl.write(json.dumps(query_to_write))
    return filename

def openai_upload_batch(client, filename, args):
    try:
        with open(filename, "rb") as f:
            batch_input_file = client.files.create(file=f, purpose="batch")

        if not batch_input_file or not getattr(batch_input_file, "id", None):
            print("Error: File upload failed.")
            return

        batch_input_file_id = batch_input_file.id
        print(f"Uploaded batch file with ID: {batch_input_file_id}")

        response = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": "nightly eval job"}
        )

        print(f"Batch request submitted successfully: {response}")

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return response 

def openai_get_results(client, response, args):
    batch_id = response.id 
    while True:
        batch_status = client.batches.retrieve(batch_id)

        if batch_status.status == "completed":
            file_response = batch_status.output_file_id
            break  
        elif batch_status.status in ["failed", "cancelled", "expired"]:
            print(f"Batch {batch_id} failed, cancelled, or expired.")
            return None 
        
        time.sleep(60)  # Wait before polling again  
    
    directory = f"batch/output/{args.type}/{args.operation}"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"batch_{args.type}_{args.operation}_{args.mode}_{args.model}_{args.prompt}_{args.T}_output.jsonl")
    result = client.files.content(file_response) 
    with open(filename, "w") as f_jsonl:
        f_jsonl.write(result.text)
    answers = [] 
    with open(filename, "r") as f_jsonl:
        for line in f_jsonl:
            data = json.loads(line)
            answer = data["response"]["body"]["choices"][0]["message"]["content"]
            answers.append(answer)
    return answers 

        
def check_status(client, batch_id):
    
    batch = client.batches.retrieve(batch_id)
    print("Current status:", batch.status)
    return batch.status
    
if __name__ == "__main__":
    client = openai.OpenAI()
    
    # print(upload_batch(client))
    
    print(check_status(client, "batch_67915dfb33c081909dbc9e0ee3047058"))