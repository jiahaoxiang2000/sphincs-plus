import subprocess
import openai
import os
from typing import List, Optional

client = openai.OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("OPENAI_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://s.lconai.com/v1"
)

def get_staged_diff() -> str:
    """Get the diff of staged changes."""
    try:
        # Get the diff of staged changes
        diff = subprocess.check_output(
            ['git', 'diff', '--cached'],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        return diff
    except subprocess.CalledProcessError:
        return ""

def generate_commit_message(diff: str, api_key: Optional[str] = None) -> str:
    """Generate a commit message using OpenAI API."""
    if not diff:
        return "No staged changes found"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": """You are a Git commit message expert. Follow these rules:
                1. Use imperative mood ('Add', not 'Added')
                2. Keep first line under 50 characters
                3. Focus on WHAT and WHY, not HOW
                4. Be clear and descriptive
                5. Follow conventional commits format when applicable
                6. Don't include file paths unless critical"""},
            {"role": "user", "content": f"Please generate a commit message for the following changes:\n\n{diff}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        message_content = response.choices[0].message.content
        return message_content.strip() if message_content else ""
    except Exception as e:
        return f"Error generating commit message: {str(e)}"

def create_commit_message() -> str:
    """Main function to generate commit message for staged changes."""
    diff = get_staged_diff()
    return generate_commit_message(diff)

if __name__ == "__main__":
    print(create_commit_message())
