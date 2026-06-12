import os
import json
import requests
import google.generativeai as genai

def get_local_codebase():
    """Collects all meaningful sources into single text block."""
    code_text = "=== CURRENT CODEBASE ===\n\n"
    # File extentions to proceed
    valid_extensions = ('.c', '.h', 'Makefile', '.mk')
    
    for root, dirs, files in os.walk('.'):
        # Except hide folders and compiled blobs/binares
        if '.git' in root or '.github' in root:
            continue
            
        for file in files:
            if file.endswith(valid_extensions) or file == 'Makefile':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        code_text += f"\n--- Файл: {filepath} ---\n{content}\n"
                except Exception:
                    pass
    return code_text

def get_fork_diff(owner, repo, target_fork, token):
    """Receives diff between own master and master of target (foreign) fork."""
    if not target_fork:
        return ""
        
    print(f"Loading diff with fork {target_fork}...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    # API request to compare: /repos/{owner}/{repo}/compare/master..{target_fork}:master
    # Which one is better there, "two dots" or "three dots" comparing? AI thinks that three dots, I think the opposite)
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/master..{target_fork.split('/')[0]}:master"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return f"\n=== DIFF WITH FOREIGN FORK ({target_fork}) ===\n\n{response.text}"
    else:
        print(f"Can't get diff: {response.status_code}")
        return ""

def create_github_issue(title, body, token, repo_full_name):
    """Create Issue with audit results."""
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Report successfully published: {response.json()['html_url']}")
    else:
        print(f"Error creating Issue: {response.status_code}")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    gh_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    target_fork = os.getenv("TARGET_FORK")
    repo_full_name = f"{repo_owner}/{repo_name}"

    if not api_key:
        print("GEMINI_API_KEY not found.")
        return

    genai.configure(api_key=api_key)

    # 1. Gathering data
    codebase = get_local_codebase()
    fork_diff = get_fork_diff(repo_owner, repo_name, target_fork, gh_token)
    
    context = codebase + fork_diff

    # 2. Forming deep system prompt
    system_prompt = """
    Ты — Senior Embedded Firmware Architect. Проведи глубокий аудит прошивки для ESP8266 (esp-link).
    Тебе предоставлена текущая кодовая база проекта. Возможно, также прикреплен diff со сторонним форком.
    
    Твои задачи:
    1. Поиск скрытых проблем: Проанализируй код на предмет утечек памяти, переполнения буферов и неэффективных циклов.
    2. Оптимизация сети и железа: Предложи способы уменьшения задержек/дропов Wi-Fi и оптимизации передачи данных в/из UART. Рассмотри hardware-level tweaks.
    3. Анализ форка (если есть diff): Изучи решения из чужого форка. Предложи, какие фичи или оптимизации стоит перенести. 
       ВАЖНО: Игнорируй изменения системы сборки (например, переезд на PlatformIO), если они не несут критической пользы для релизных таргетов. Не предлагай удалять существующий функционал без веских технических обоснований.
    4. Архитектура: Оцени структуру проекта и предложи варианты рефакторинга для повышения стабильности.

    Отвечай в строгом формате Markdown. Сделай ответ структурированным:
    - 🚨 Критические уязвимости и баги (если есть)
    - ⚡ Оптимизация Wi-Fi и UART
    - 🔄 Анализ стороннего форка (что взять, что игнорировать)
    - 🛠 Рекомендации по рефакторингу
    """

    full_prompt = f"{system_prompt}\n\nContext for analisys:\n{context}"

    try:
        # For that (huge) volume using the "heaviest" model
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            generation_config={"temperature": 0.2}
        )
        
        print("Sending data to Gemini (this may take a while, usually around a minute)...")
        response = model.generate_content(full_prompt)
        
        # 3. Publushing results
        issue_title = f"🤖 AI Audit Report: Internal analysis"
        if target_fork:
            issue_title += f" & Comparing with {target_fork}"
            
        create_github_issue(issue_title, response.text, gh_token, repo_full_name)
        
    except Exception as e:
        print(f"Error processing: {e}")

if __name__ == "__main__":
    main()