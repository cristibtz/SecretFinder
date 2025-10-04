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

def get_repo_last_commits(repo, no_commits):
    try:
        prev_commits = list(repo.iter_commits(all=True, max_count=no_commits))
        return prev_commits
        print(prev_commits)
    except Exception as e:
        print("Error: ", str(e))

def get_commit_files_with_changes(commit):
    try:
        if len(commit.parents) == 0:
            return commit.diff(None)
        else:
            diff = commit.diff(commit.parents[0])

        print(f"\n--- Commmit: {commit.hexsha[:8]} ---")
        print(f"Author: {commit.author.name}")
        print(f"Message: {commit.message.strip()}")
        print(f"Files changed: {len(diff)}")

        for change in diff:
            file_name = change.a_path if change.a_path else change.b_path
            print(f"\nFile '{file_name}':")

            if change.change_type == "A":
                print(" Status: Added")
            elif change.change_type == "D":
                print(" Status: Deleted")
            elif change.change_type == "M":
                print(" Status: Modified")
            elif change.change_type == "R":
                print(f" Status: Renamed from {change.a_path} to {change.b_path}")
            
            try:
                import subprocess
                result = subprocess.run([
                    'git', 'show', '--numstat', '--format=', commit.hexsha, '--', file_name
                ], capture_output=True, text=True, cwd=commit.repo.working_dir)
                
                if result.returncode == 0 and result.stdout.strip():

                    parts = result.stdout.strip().split('\t')
                    if len(parts) >= 2:
                        additions = parts[0] if parts[0] != '-' else '0'
                        deletions = parts[1] if parts[1] != '-' else '0'
                        print(f" Added lines: {additions}")
                        print(f" Removed lines: {deletions}")
                    else:
                        print("  Binary file or no changes detected")
                else:
                    print("  Could not get line count")
            except Exception as e:
                print(f"  Error getting stats: {e}")

            try:
                result = ""
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
                        print(" Removed lines:")
                        for line in enumerate[:10]:
                            print(f"    - {line}")
                        if len(removed_lines) > 10:
                            result += f"    ... and {len(removed_lines) - 10} more removed lines"

                    if added_lines:
                        print(" Added lines:")
                        for line in added_lines[:10]:
                            print(f"    + {line}")
                        if len(added_lines) > 10:
                            result += f"    ... and {len(added_lines) - 10} more added lines"
                
                return result
            except Exception as e:
                print("Error: ", str(e))
    except Exception as e:
        print("Error: ", str(e))

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

        prev_commits = get_repo_last_commits(repo, no_commits)
        for commit in prev_commits:
            result = get_commit_files_with_changes(commit)
            print(result)

        # Start scanning with LLM
        llm_scan()
    else:
        if check_repo_exists(repo_path):
            print("Repository exists locally and has .git folder")
            repo = Repo(repo_path)
            print(repo)

            prev_commits = get_repo_last_commits(repo, no_commits)
            for commit in prev_commits:
                result = get_commit_files_with_changes(commit)
                print(result)

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