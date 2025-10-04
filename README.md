# Repository-Secret-Scanner-using-LLMs
Check for hardcoded secrets in a Git repository using LLMs

## Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/cristibtz/SecretFinder.git
    cd SecretFinder
    ```
2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```
4. Set up your OpenAI API key in a `.env` file:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key_here
    ```
## Usage
Run the tool with a Git repository URL or a local path:
```bash
secret-finder --repo /home/alex/my-repo
# or
secret-finder --repo https://github.com/cristibtz/SecretFinder.git
# or
secret-finder --repo git@github.com:cristibtz/SecretFinder.git
# or
secret-finder --repo ./ --n 20 --output file.json
```
