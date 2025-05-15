import openai
import anthropic 
from anthropic import Anthropic
import os
import numpy as np
import json
import re
import time
import instructor # for claude formatting 
from openai import OpenAI
from datetime import datetime, timedelta, timezone
from tiktoken import encoding_for_model, get_encoding
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama

model_list = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "o1", "o1-mini", "o3-mini", "o4-mini", "gpt-4.1-2025-04-14", "o4-mini-2025-04-16",
              "llama3.3", "llama3.2", 
              "deepseek-chat", "deepseek-reasoner",
              "gemini-1.5-pro", "gemini-2.0-flash-001", "gemini-2.0-flash-lite-preview-02-05", "gemini-2.5-flash-preview-04-17",
              "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307", "claude-3-7-sonnet-20250219"]     
prompt_list = ["none", "k-shot", "CoT", "0-CoT", "AnsOnly"]

def translate(q, q_state='', args=None):
    Q = q_state 
    prompt_folder = "prompt"
    if args.prompt in ["CoT", "k-shot"]:
        with open(f"prompt/{args.type}/{args.operation}/" + prompt_folder + "/" + args.prompt + "-prompt.txt", "r") as f:
            exemplar = f.read()
        Q = Q + exemplar + "\n\n\n"

    Q = Q + q

    match args.prompt:
        case "0-CoT":
            Q = Q + " Let's think step by step: \n"
        case "AnsOnly":
            Q = Q + "No additional text needed. \n"

    Q = Q + f"Answer the question in {args.token} tokens. \n"

    Q = Q + "A: "

    return Q


def extract_json(text: str):
    """
    Return the first {...} block in `text` as a Python object.
    Raises ValueError if none found or JSON is malformed.
    """
    match = re.search(r"\{.*\}", text, flags=re.S)   # greedy → outermost braces
    if not match:
        raise ValueError("No JSON object found")
    return match.group()

# @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(1000))
def predict(Q, args, response_format=None):
    inputs = Q
    Answer_list = []

    if "gpt" in args.model or "o1" in args.model or "o3" in args.model or "o4" in args.model:
        client = openai.OpenAI(
            api_key = os.getenv("OPENAI_API_KEY")
        )
    elif "llama" in args.model:
        client = openai.OpenAI(
            api_key = os.getenv("LLAMA_API_KEY"),
            base_url = "https://api.llama-api.com"
        )
    elif "deepseek-chat" in args.model:
        client = openai.OpenAI(
            api_key = os.getenv("DEEPSEEK_API_KEY"),
            base_url = "https://api.deepseek.com"
        )
    elif "gemini" in args.model:
        client = openai.OpenAI(
            api_key = os.getenv("GEMINI_API_KEY"),
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    elif "claude-3-7" in args.model:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        client = instructor.from_anthropic(client, 
            mode=instructor.Mode.ANTHROPIC_REASONING_TOOLS)
        
    elif "claude" in args.model:
        client = instructor.from_anthropic(
            anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
                ),
        )
    elif "deepseek-reasoner" in args.model:
        client = instructor.from_openai(
            OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"),
            mode=instructor.Mode.MD_JSON,
        )


    for text in inputs:
        if "claude-3-7" in args.model:
            try:
                response = client.chat.completions.create(
                    model=args.model,
                    messages=[
                        {"role": "assistant", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    temperature=1,
                    max_tokens=args.token,
                    stream=False, 
                    timeout=30, 
                    response_model=response_format if response_format else None,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": int(args.token * 4/5)
                    },
                )
                Answer_list.append(json.dumps(response.model_dump(mode='json')))
            except Exception as e:
                print(f"Error: {e}")
                Answer_list.append(json.dumps("Error"))
        elif "claude" in args.model:
            try:
                response = client.messages.create(
                    model=args.model,
                    messages=[
                        {"role": "assistant", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    temperature=args.T,
                    max_tokens=args.token,
                    stream=False, 
                    timeout=30, 
                    response_model=response_format if response_format else None,
                )
                Answer_list.append(json.dumps(response.model_dump(mode='json')))
            except Exception as e:
                print(f"Error: {e}")
                Answer_list.append(json.dumps("Error"))
        elif "llama" in args.model:
            llm = Ollama(model=args.model, request_timeout=120.0)
            sllm = llm.as_structured_llm(response_format)
            try: 
                response = sllm.chat(
                    messages = [
                    ChatMessage(
                        role="system", content="You are a helpful assistant."
                    ),
                    ChatMessage(role="user", content=text),
                    ],
                    request_timeout=600,
                )
                Answer_list.append(response.message.content)
            except Exception as e:
                print(e)
                Answer_list.append("\{'final_answer': -1\}")
        elif "o3" in args.model or "o4" in args.model:
            try:
                response = client.beta.chat.completions.parse(
                    model=args.model,
                    messages=[
                        {"role": "developer", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    max_completion_tokens=args.token,
                    timeout=60,
                    response_format=response_format,
                )
                Answer_list.append(response.choices[0].message.content) 
            except openai.LengthFinishReasonError:
                print("Token limit exceeds.")
                Answer_list.append("\{'final_answer': -1\}")
        elif "deepseek-chat" in args.model:
            try:
                response = client.beta.chat.completions.parse(
                    model=args.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    temperature=args.T,
                    max_tokens=args.token,
                    timeout=60,
                    response_format={'type': 'json_object'},
                )
                tokenizer = get_encoding("cl100k_base")
                print("Number of tokens:", len(tokenizer.encode(response.choices[0].message.content))) 
                Answer_list.append(response.choices[0].message.content)
            except openai.LengthFinishReasonError:
                print("Token limit exceeds.")
                Answer_list.append("\{'final_answer': -1\}")
        elif "deepseek-reasoner" in args.model:
            try:
                _, response = client.chat.completions.create_with_completion(
                    model=args.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    temperature=args.T,
                    max_tokens=args.token,
                    timeout=60,
                    response_model=response_format,
                )
                tokenizer = get_encoding("cl100k_base")
                print("Number of tokens:", len(tokenizer.encode(response.choices[0].message.content))) 
                ans = extract_json(response.choices[0].message.content)
                Answer_list.append(ans)
            except openai.LengthFinishReasonError:
                print("Token limit exceeds.")
                Answer_list.append("\{'final_answer': -1\}")
        elif response_format:
            try:
                response = client.beta.chat.completions.parse(
                    model=args.model,
                    messages=[
                        {"role": "developer", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text},
                    ],
                    temperature=args.T,
                    max_tokens=args.token,
                    timeout=60,
                    response_format=response_format,
                )
                tokenizer = get_encoding("cl100k_base")
                print("Number of tokens:", len(tokenizer.encode(response.choices[0].message.content))) 
                Answer_list.append(response.choices[0].message.content)
            except openai.LengthFinishReasonError:
                print("Token limit exceeds.")
                Answer_list.append("\{'final_answer': -1\}")
        else:
            raise ValueError("No response format provided. Maybe we want to implement None type later if some model we want to test does not support Pydantic model.")

    return Answer_list


def log(Q_list, res, partial_res, answer, args):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    time = bj_dt.now().strftime("%Y%m%d---%H-%M")
    newpath = f'log/{args.type}/{args.operation}/{args.model}-{args.mode}-T{str(args.T)}-token{str(args.token)}-{time}-{args.prompt}-{args.description}'  
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = newpath + "/"
    with open(newpath + "res.txt", "w") as f:
        for r in res:
            f.write(f"{r}\n")
    with open(newpath + "partial_res.txt", "w") as f:
        for r in partial_res:
            f.write(f"{r}\n")
    with open(newpath + "answer.txt", "w") as f:
        for a in answer:
            f.write(f"{a}\n\n\n")
    res = np.array(res)
    partial_res = np.array(partial_res)
    with open(newpath + "prompt.txt", "w") as f:
        f.write(Q_list[0])
        f.write("\n")
        f.write("Acc: " + str(res.sum()) + '/' + str(len(res)) + '\n')
        f.write(f"Accuracy = {res.sum() / len(res)} \n")
        f.write("Partial Acc: " + str(partial_res.sum()) + '/' + str(len(partial_res)) + '\n')
        f.write(f"Partial Accuracy = {partial_res.sum() / len(partial_res)} \n")
        print(args, file=f)



 