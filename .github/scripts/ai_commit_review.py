import os
import requests
from google import genai
from google.genai import types

def post_commit_comment(repo_full_name, commit_sha, token, body):
    """Send comment directly to exact commit."""
    url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": body}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ Comment to commit {commit_sha[:7]} susessfully added.")
    else:
        print(f"❌ Error comment publising: {response.status_code} - {response.text}")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    gh_token = os.getenv("GITHUB_TOKEN")
    commit_sha = os.getenv("COMMIT_SHA")
    repo_full_name = os.getenv("REPO_FULL_NAME")
    commit_msg = os.getenv("COMMIT_MSG", "Без описания")

    if not all([api_key, gh_token, commit_sha, repo_full_name]):
        print("Error: missing necessary env vars.")
        return

    # Reading diff
    try:
        with open("commit_diff.txt", "r", encoding="utf-8") as f:
            diff_content = f.read()
    except FileNotFoundError:
        print("File commit_diff.txt not found. Skip.")
        return

    if not diff_content.strip():
        print("No significant changes to analyze (it's possible that only the excluded files have changed).")
        return

    # Protecionn from huge commits (btw Flash Lite can a lot)
    if len(diff_content) > 100000:
        diff_content = diff_content[:100000] + "\n\n...[Diff truncated]..."

    system_prompt = """
    Ты — Embedded Code Reviewer. Оцени данный git diff. 
    Фокус: поиск опечаток, утечек памяти, логических ошибок в C/C++ (ESP8266/RP2040) и уязвимостей.
    Отвечай коротко и по делу. Если всё выглядит отлично, напиши: "✅ Проблем не обнаружено. Хороший коммит."
    """

    full_prompt = f"{system_prompt}\n\nCommit message: {commit_msg}\n\nИзменения:\n{diff_content}"

    # Init new ver client
    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(temperature=0.1)

    print(f"Commit analysis {commit_sha[:7]} with gemini-3.1-flash-lite...")

    try:
        # Select light target model
        # Note: If the API returns an error stating that the model cannot be found, 
        # check the exact spelling of the alias in Google AI Studio (sometimes they replace hyphens with periods)
        model_id = 'gemini-3.1-flash-lite' 

        response = client.models.generate_content(
            model=model_id,
            contents=full_prompt,
            config=config
        )

        # Create a final message
        final_comment = f"🤖 **Flash Lite Review**\n\n{response.text}"

        # Sent to GitHub
        post_commit_comment(repo_full_name, commit_sha, gh_token, final_comment)

    except Exception as e:
        print(f"Critical API call error: {e}")

if __name__ == "__main__":
    main()
