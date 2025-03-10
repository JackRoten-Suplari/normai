import anthropic
import time
import dotenv
import os
import json
from typing import Dict, List, Any, Optional

import argparse

MODEL_NAME = "claude-3-5-sonnet-20241022"

def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """
    Read a JSONL file and return a list of JSON objects.
    
    Args:
        file_path: Path to the JSONL file
        
    Returns:
        List of JSON objects
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {line}")
                    print(f"Error details: {e}")
                    continue
    return data

def list_batches():
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    return client.messages.batches.list()

def create_batch():
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    openai_requests = read_jsonl('data/boots-output.batch_1_of_1.jsonl')
    requests = []
    i =1
    for r in openai_requests:
        m = {
                'custom_id':f'norm-{i}',
                'params':{
                    'model': MODEL_NAME,
                    'max_tokens':2000,
                    'messages':[
                        {'role':'assistant', 'content':r['body']['messages'][0]['content']},
                        r['body']['messages'][1]
                    ]
                }
            }
    
        requests.append(m)
        i+=1

    response = client.beta.messages.batches.create(
        requests=requests
    )
    return response

def get_batch(id):
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    return client.messages.batches.retrieve(id)

def main():
    parser = argparse.ArgumentParser(description="Process a JSONL file with the OpenAI batch API")
    parser.add_argument('--action', help='create or list',default='create')
    parser.add_argument('--id', help='id of batch to get')

    args = parser.parse_args()
    if args.action == 'create':
        response = create_batch()
        print(f"Batch ID: {response.id}")
        print(f"Status: {response.processing_status}")

        print(f"Created at: {response.created_at}")

    elif args.action == 'list':
        response = list_batches()
        print(response.model_dump_json(indent=4))
        
    elif args.action == 'retreive':
        print(get_batch(args.id))

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()


   
