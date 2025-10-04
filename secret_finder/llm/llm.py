from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

system_message = "You are an assistant that scans git repo commits and diffs and looks for secrets. "
system_message += "Always look for secrets in added or delete lines of code, like API keys, passwords, tokens, private keys, etc. "
system_message += "Respond in JSON format and include the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence"

data = ""

def user_prompt_for(data):
    user_prompt = "Analyze the following git commit diffs and identify any potential secrets such as API keys, passwords, tokens, or private keys. "
    user_prompt += "Provide your response in JSON format with the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence.\n\n"
    user_prompt += "Here are the commit diffs to analyze:\n\n"
    user_prompt += data
    return user_prompt

class SecretFinding(BaseModel):
    commit_hash: str
    file_path: str
    snippet: str
    finding_type: str
    confidence: str

class ScanResult(BaseModel):
    findings: List[SecretFinding]

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=system_message
)

result = agent.run_sync(user_prompt_for(data))
print(result.output) 