from dotenv import load_dotenv
from pydantic_ai import Agent
from typing import List
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Create user prompt
def user_prompt_for(data):
    user_prompt = "Analyze the following git commit diffs and identify any potential hardcoded secrets such as API keys, passwords, tokens, or private keys. "
    user_prompt += "Provide your response in JSON format with the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence.\n\n"
    user_prompt += "Here are the commit diffs to analyze:\n\n"
    user_prompt += data
    return user_prompt
    
# Scan diffs with LLM
def llm_scan(data):
    import asyncio
    
    system_message = "You are an assistant that scans git repo commits and diffs and looks for hardcoded secrets. "
    system_message += "Always look for hardcoded secrets in added or delete lines of code, like API keys, passwords, tokens, private keys, etc. "
    system_message += "Ignore placeholder values for secrets and only focus on secrets that look real. "
    system_message += "Respond in JSON format and include the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence. "
    system_message += "If no secrets are found, you must respond with JSON response {'result': 'No secrets found'}"

    agent = Agent(
        'openai:gpt-5',
        system_prompt=system_message
    )

    try:
        result = agent.run_sync(user_prompt_for(data))
        
        text = result.output

        return text

    except Exception as e:
        return f"Error: {str(e)}"
    