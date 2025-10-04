import argparse
from git import *
import os
from secret_finder.llm.llm import llm_scan
import json

# Check if repo path exists locally
def check_repo_exists(repo_path):
    if os.path.isdir(repo_path) and os.path.isdir(f"{repo_path}/.git/"):
        return True
    else:
        return False

# Clone the repo and save it in /tmp
def clone_repo(repo_url):
    try:

        repo_name = repo_url.split("/")[-1].replace(".git", "")

        local_path = f"/tmp/{repo_name}"

        if os.path.exists(local_path):
            import shutil
            shutil.rmtree(local_path)

        repo = Repo.clone_from(repo_url, local_path)   

        print("Repository cloned successfully in: ", local_path)

        return repo 

    except Exception as e:
        print("Error: ", str(e))
        return None

# Get last n commits
def get_repo_last_commits(repo, no_commits):
    try:
        prev_commits = list(repo.iter_commits(all=True, max_count=no_commits))
        return prev_commits
        print(prev_commits)
    except Exception as e:
        print("Error: ", str(e))

# Output results to json file
def output_to_json(repo_path, output, output_file):
    try:
        final_output = {
            "scanned_repo": repo_path,
            "findings": json.loads(output.replace("```json", "").replace("```", ""))
        }
        
        with open(output_file, "w") as f:
            json.dump(final_output, f, indent=4)

        print(f"Output saved to {output_file}")

    except Exception as e:
        print("Error: ", str(e))

# Get commit file changes(Added, Deleted, Modified, Renamed) along with line changes
def get_commit_files_with_changes(commit):
    result = ""
    try:
        if len(commit.parents) == 0:
            empty_tree = commit.repo.tree('4b825dc642cb6eb9a060e54bf8d69288fbee4904')
            diff = empty_tree.diff(commit.tree)
        else:
            diff = commit.parents[0].diff(commit)

        result += f"\n--- Commmit: {commit.hexsha[:8]} ---\n"
        result += f"Author: {commit.author.name}\n"
        result += f"Message: {commit.message.strip()}\n"
        result += f"Files changed: {len(diff)}\n"

        for change in diff:
            file_name = change.a_path if change.a_path else change.b_path
            result += f"\nFile '{file_name}':\n"

            if change.change_type == "A":
                result += " Status: Added\n"
            elif change.change_type == "D":
                result += " Status: Deleted\n"
            elif change.change_type == "M":
                result += " Status: Modified\n"
            elif change.change_type == "R":
                result += f" Status: Renamed from {change.a_path} to {change.b_path}\n"
            
            try:
                import subprocess
                subprocess_result = subprocess.run([
                    'git', 'show', '--numstat', '--format=', commit.hexsha, '--', file_name
                ], capture_output=True, text=True, cwd=commit.repo.working_dir)
                
                if subprocess_result.returncode == 0 and subprocess_result.stdout.strip():

                    parts = subprocess_result.stdout.strip().split('\t')
                    if len(parts) >= 2:
                        additions = parts[0] if parts[0] != '-' else '0'
                        deletions = parts[1] if parts[1] != '-' else '0'
                        result += f" Added lines: {additions}\n"
                        result += f" Removed lines: {deletions}\n"
                    else:
                        result += "  Binary file or no changes detected\n"
                else:
                    result += "  Could not get line count\n"
            except Exception as e:
                result += f"  Error getting stats: {e}\n"

            try:
                diff_result = subprocess.run([
                    'git', 'show', '--format=', commit.hexsha, '--', file_name
                ], capture_output=True, text=True, cwd=commit.repo.working_dir)

                if diff_result.returncode == 0 and diff_result.stdout:
                    diff_content = diff_result.stdout
                    lines = diff_content.split('\n')

                    added_lines = []
                    removed_lines = []

                    for line in lines:
                        if line.startswith('+') and not line.startswith('+++'):
                            added_lines.append(line[1:])
                        elif line.startswith('-') and not line.startswith('---'):
                            removed_lines.append(line[1:])

                    if removed_lines:
                        result += " Removed lines:\n"
                        for line in removed_lines[:10]:
                            result += f"    - {line}\n"
                        if len(removed_lines) > 10:
                            result += f"    ... and {len(removed_lines) - 10} more removed lines\n"

                    if added_lines:
                        result += " Added lines:\n"
                        for line in added_lines[:10]:
                            result += f"    + {line}\n"
                        if len(added_lines) > 10:
                            result += f"    ... and {len(added_lines) - 10} more added lines\n"
                
            except Exception as e:
                result += f"Error: {str(e)}\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Scan secrets function that aggregates all functionalities
def scan_secrets(repo_path, no_commits, output_file):
    print("-" * 40)
    print(f"Scanning repository: {repo_path}")
    print(f"Number of commits to scan: {no_commits}")
    print(f"Output will be saved to: {output_file}")
    print("-" * 40)
    print("\n")

    result = ""

    if repo_path.startswith("https://") or repo_path.startswith("git@") and repo_path.endswith(".git"):

        print("Repository URL detected")

        repo = clone_repo(repo_path)

        print("Gathering commits and diffs...")
        prev_commits = get_repo_last_commits(repo, no_commits)
        for commit in prev_commits:
            result += get_commit_files_with_changes(commit)

        print("Analyzing diffs with LLM...")
        result = llm_scan(result)

        print("Saving results to JSON...")
        output_to_json(repo_path, result, output_file)

    else:
        if check_repo_exists(repo_path):
            print("Repository exists locally and has .git folder")

            repo = Repo(repo_path)

            print("Gathering commits and diffs...")
            prev_commits = get_repo_last_commits(repo, no_commits)
            for commit in prev_commits:
                result += get_commit_files_with_changes(commit)

            print("Analyzing diffs with LLM...")
            result = llm_scan(result)

            print("Saving results to JSON...")
            output_to_json(repo_path, result, output_file)

        else:
            print("Repository doesn't exist locally or the provided path is not a git repository")
            print("Please provide proper a repository URL or clone it yourself!")

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