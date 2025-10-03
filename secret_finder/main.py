import argparse
from git import *
import os

def llm_scan():
    pass

def check_repo_exists(repo_path):
    if os.path.isdir(repo_path) and os.path.isdir(f"{repo_path}/.git/"):
        return True
    else:
        return False

def clone_repo(repo_url):
    try:

        repo_name = repo_url.split("/")[-1].replace(".git", "")

        local_path = f"/tmp/{repo_name}"

        if os.path.exists(local_path):
            import shutil
            shutil.rmtree(local_path)

        repo = Repo.clone_from(repo_url, local_path)   

        print("Repo cloned")

        return repo 

    except Exception as e:
        print("Error: ", str(e))
        return None

def get_repo_last_commits():
    pass

def scan_secrets(repo_path, no_commits, output_file):
    print("-" * 40)
    print(f"Scanning repository: {repo_path}")
    print(f"Number of commits to scan: {no_commits}")
    print(f"Output will be saved to: {output_file}")
    print("-" * 40)
    print("\n")

    if repo_path.startswith("https://") or repo_path.startswith("git@") and repo_path.endswith(".git"):
        print("Repository URL detected")
        repo = clone_repo(repo_path)
        print(repo)
        # Start scanning with LLM
        llm_scan()
    else:
        if check_repo_exists(repo_path):
            print("Repository exists locally and has .git folder")
            # Start scanning with LLM
            llm_scan()
        else:
            print("Repository doesn't exist locally or provided path is not a git repo")
            print("Please provide proper repoitory url or clone it yourself!")



def main():
    parser = argparse.ArgumentParser(description="Secret Finder Tool")
    parser.add_argument("--repo", type=str, required=True, help="path/url to the repository")
    parser.add_argument("--n", type=int, help="number of commits to scan", default=10)
    parser.add_argument("--out", type=str, help="output file path", default="output.json")

    args = parser.parse_args()

    repo_path = args.repo
    no_commits = args.n
    output_file = args.out

    scan_secrets(repo_path, no_commits, output_file)


if __name__ == "__main__":
    main()