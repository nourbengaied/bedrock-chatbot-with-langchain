import boto3
from typing import Dict, List, Tuple
from dataclasses import dataclass
from app.config import system_prompt_builder

# AWS configuration
PROFILE_NAME = "fireminddev"
REGION_NAME = "eu-west-2"
session = boto3.Session(profile_name=PROFILE_NAME, region_name=REGION_NAME)
bedrock = session.client("bedrock-runtime", region_name="us-east-1")

# Define your model IDs
MODEL_IDS = {
    "sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "sonnet-3.5": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "sonnet-3.5-arn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
}

@dataclass
class BedrockMetadata:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency: float

def update_metadata(metadata: BedrockMetadata, new_metadata: Dict[str, int]):
    metadata.input_tokens += new_metadata['input_tokens']
    metadata.output_tokens += new_metadata['output_tokens']
    metadata.total_tokens += new_metadata['total_tokens']
    metadata.latency += new_metadata['latency']

def invoke_bedrock(model_id, messages_list_tool_use, system_prompt, tool_config): 
    temperature = tool_config.get('temperature', 0.2)
    top_p = tool_config.get('top_p', 0) 
    top_k = tool_config.get('top_k', 50) 

    inference_config = {
        "temperature": temperature, 
        "maxTokens": tool_config.get('max_tokens', 4000),
        "topP": top_p
    }
    
    additional_model_request_fields = {
        "top_k": top_k
    }
    
    response = bedrock.converse(
        modelId=model_id, 
        messages=messages_list_tool_use, 
        system=system_prompt, 
        inferenceConfig=inference_config, 
        additionalModelRequestFields=additional_model_request_fields)

    input_tokens = float(response['usage']["inputTokens"])
    output_tokens = float(response['usage']["outputTokens"])
    total_tokens = float(response['usage']["totalTokens"])
    latency = float(response['metrics']['latencyMs'])

    bedrock_metadata = {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens, 
        'total_tokens': total_tokens, 
        'latency': latency
    }
    return response, bedrock_metadata

def generate_conversation(model_id, system_prompt, messages_list, tool_config):
    messages_list_tool_use = [message for message in messages_list]

    metadata = BedrockMetadata(input_tokens=0, output_tokens=0, total_tokens=0, latency=0)

    response, bedrock_metadata = invoke_bedrock(model_id, messages_list_tool_use, system_prompt, tool_config)

    update_metadata(metadata, bedrock_metadata)
    
    final_response = response['output']['message']['content'][0]['text']
    
    return final_response

def chat(session_id, user_msg, model_id, customer_id, tool_config):
    try:
        messages_list = st.session_state.get('messages_list', [])

        messages_list.append({'role': 'user', 'content': [{'text': user_msg}]})
        
        system_prompt_str = system_prompt_builder()
        system_prompt = [{'text': system_prompt_str}]
        
        assistant_response = generate_conversation(
            MODEL_IDS[model_id], system_prompt, messages_list, tool_config)
                
        messages_list.append({'role': 'assistant', 'content': [{'text': assistant_response}]})
        
        st.session_state['messages_list'] = messages_list

        return assistant_response, messages_list

    except Exception as e:
        print(f"Error: {e}")
        return None, []

def clear_session_state():
    st.session_state['messages_list'] = []

def format_messages(messages_list):
    formatted_messages = ""
    for message in messages_list:
        role = message['role']
        text = message['content'][0]['text']
        formatted_messages += f"{role.capitalize()}: {text}\n\n"
    return formatted_messages
