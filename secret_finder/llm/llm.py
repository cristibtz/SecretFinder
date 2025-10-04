from huggingface_hub import login, InferenceClient
from transformers import AutoTokenizer
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

hf_token = os.environ['HF_TOKEN']
login(hf_token, add_to_git_credential=True)

model_id = "AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
BARON_LLM_URL = "https://qim40hw4fzpol7yt.us-east-1.aws.endpoints.huggingface.cloud"

system_message = "You are an assistant that scans git repo commits and diffs and looks for secrets. "
system_message += "Always look for secrets in added or delete lines of code, like API keys, passwords, tokens, private keys, etc. "
system_message += "Respond in JSON format and include the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence"

def user_prompt_for(data):
    user_prompt = "Analyze the following git commit diffs and identify any potential secrets such as API keys, passwords, tokens, or private keys. "
    user_prompt += "Provide your response in JSON format with the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence.\n\n"
    user_prompt += "Here are the commit diffs to analyze:\n\n"
    user_prompt += data
    return user_prompt

def messages_for(data):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for(data)}
    ]

tokenizer = AutoTokenizer.from_pretrained(code_qwen)
messages = messages_for(pi)
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

print(text)