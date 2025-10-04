from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

system_message = "You are an assistant that scans git repo commits and diffs and looks for secrets. "
system_message += "Always look for secrets in added or delete lines of code, like API keys, passwords, tokens, private keys, etc. "
system_message += "Respond in JSON format and include the following fields: commit hash, file path, line/offset or snippet, finding type, and a brief rationale/confidence"

data = """
----------------------------------------
Scanning repository: ./
Number of commits to scan: 10
Output will be saved to: output.json
----------------------------------------


Repository exists locally and has .git folder
<git.repo.base.Repo '/home/cristibtz/SecretFinder/.git'>

--- Commmit: c53ff3a4 ---
Author: Cristian Branet
Message: Added git commit and diff listing and working on LLM
Files changed: 4

File '.env.example':
 Status: Deleted
 Added lines: 1
 Removed lines: 0
 Added lines:
    + HF_TOKEN=hftoken

File 'secret_finder/llm/__init__.py':
 Status: Deleted
 Added lines: 0
 Removed lines: 0

File 'secret_finder/llm/llm.py':
 Status: Deleted
 Added lines: 35
 Removed lines: 0
 Added lines:
    + from huggingface_hub import login, InferenceClient
    + from transformers import AutoTokenizer
    + from dotenv import load_dotenv
    + import os
    + 
    + load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
    + 
    + hf_token = os.environ['HF_TOKEN']
    + login(hf_token, add_to_git_credential=True)
    + 
    ... and 25 more added lines

File 'secret_finder/main.py':
 Status: Modified
 Added lines: 99
 Removed lines: 5
 Removed lines:
    - *enumerate[slice(None, 10, None)]
 Added lines:
    +     try:
    +         prev_commits = list(repo.iter_commits(all=True, max_count=no_commits))
    +         return prev_commits
    +         print(prev_commits)
    +     except Exception as e:
    +         print("Error: ", str(e))
    + 
    + def get_commit_files_with_changes(commit):
    +     try:
    +         if len(commit.parents) == 0:
    ... and 89 more added lines

--- Commmit: 2b6e1c0e ---
Author: Cristian Branet
Message: Added get last no of commits
Files changed: 1

File 'secret_finder/main.py':
 Status: Modified
 Added lines: 8
 Removed lines: 2
 Removed lines:
    - *enumerate[slice(None, 10, None)]
 Added lines:
    + def get_repo_last_commits(repo, no_commits):
    +     prev_commits = list(repo.iter_commits(all=True, max_count=no_commits))
    +     print(prev_commits)
    +         get_repo_last_commits(repo, no_commits)
    +             repo = Repo(repo_path)
    +             print(repo)
    +             get_repo_last_commits(repo, no_commits)
    + 

--- Commmit: b169c506 ---
Author: Cristian Branet
Message: initial functions
Files changed: 5

File 'LICENSE':
 Status: Deleted
 Added lines: 0
 Removed lines: 0

File 'requirements.txt':
 Status: Deleted
 Added lines: 1
 Removed lines: 0
 Added lines:
    + GitPython

File 'secret_finder/__init__.py':
 Status: Deleted
 Added lines: 0
 Removed lines: 0

File 'secret_finder/main.py':
 Status: Deleted
 Added lines: 79
 Removed lines: 0
 Added lines:
    + import argparse
    + from git import *
    + import os
    + 
    + def llm_scan():
    +     pass
    + 
    + def check_repo_exists(repo_path):
    +     if os.path.isdir(repo_path) and os.path.isdir(f"{repo_path}/.git/"):
    +         return True
    ... and 69 more added lines

File 'setup.py':
 Status: Deleted
 Added lines: 13
 Removed lines: 0
 Added lines:
    + from setuptools import setup
    + 
    + setup(
    +     name='secret-finder',
    +     version='0.0.1',
    +     description='Secret Finder Tool',
    +     author='Cristian Branet',
    +     author_email='branet.cristian@gmail.com',
    +     packages=['secret_finder'],
    +     entry_points={
    ... and 3 more added lines
"""

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