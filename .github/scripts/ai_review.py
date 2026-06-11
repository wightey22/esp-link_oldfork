import os
import google.generativeai as genai

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not defined")
        return

    # Initialize Gemini
    genai.configure(api_key=api_key)

    with open("pr_diff.txt", "r", encoding="utf-8") as f:
        diff_content = f.read()

    # Gemini has a huge context window, so we can safely increase symbols limit
    if len(diff_content) > 150000:
        diff_content = diff_content[:150000] + "\n\n...[Diff truncated due to size limits]..."

    system_prompt = """
    Ты — Senior Fullstack Engineer и System Architect. Проведи экспертное код-ревью предоставленного Git diff.
    Сконцентрируйся на критических багах, утечках памяти, оптимизации алгоритмов, чистом коде и безопасности.
    
    Формат ответа:
    - Используй строгий Markdown на русском языке.
    - Пиши кратко и по делу.
    - Ошибки оформляй списком: Файл/строка -> Что не так -> Как исправить (с примером исправленного кода).
    """

    # Colloect all request body together (Gemini clearly understand commands and data combinations)
    full_prompt = f"{system_prompt}\n\nВот изменения в Pull Request, которые нужно проанализировать:\n\n{diff_content}"

    try:
        # Using tax-free and fast model gemini-2.5-flash
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"temperature": 0.1} # for code analysis always use 'temperature' 0.1 or 0.2 to prevent "fantasies"
        )
        response = model.generate_content(full_prompt)
        
        with open("ai_response.md", "w", encoding="utf-8") as rf:
            rf.write(response.text)
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

if __name__ == "__main__":
    main()