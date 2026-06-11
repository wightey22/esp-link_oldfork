import os
import google.generativeai as genai

def determine_model(diff_text, pr_title):
    """
    "smart" model select depends on context of Pull Request.
    """
    # Marks in PR naming which indicies that lighter model is enough for
    light_keywords = ['docs:', 'chore:', 'style:', 'minor:', 'readme', 'fix typo']
    title_lower = pr_title.lower() if pr_title else ""
    
    # 1. Checking header
    if any(kw in title_lower for kw in light_keywords):
        return "gemini-3.1-flash-lite", "Lighter model selected (based on PR header tags)"
        
    # 2. Checking diff size (for ex, less 3000 symbols — that expect equals around 50-80 code lines)
    if len(diff_text) < 3000:
        return "gemini-3.1-flash-lite", "Lighter model selected (due to small amount of changes)"
        
    # All other cases using the main (the "flagship" among accessible models)
    return "gemini-3.5-flash", "Heavier (main) model selected (complex or high-volume code)"

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    pr_title = os.getenv("PR_TITLE", "")

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

    # Routing model
    model_name, routing_reason = determine_model(diff_content, pr_title)
    print(f"Routing: {routing_reason} -> {model_name}")

    system_prompt = """
    Ты — Senior Embedded & Systems Engineer. Проведи жесткое, экспертное код-ревью предоставленного Git diff.
    Твоя специализация: C/C++, микроконтроллеры (ESP8266, ESP32, RP2040), а также низкоуровневая разработка под Linux (U-Boot, Device Tree, ядра для ARM/MIPS/Marvell SoC).
    
    Особое внимание удели:
    1. Утечкам памяти, переполнениям буфера и работе с указателями.
    2. Оптимизации производительности и размера бинарника (для MCU).
    3. Аппаратно-зависимым ошибкам (работа с регистрами, прерываниями, таймерами, watchdog).
    4. Чистоте архитектуры и соответствию стандартам.

    Формат ответа (строгий Markdown на русском):
    - Пиши емко, без лишней "воды".
    - Ошибки оформляй списком: Файл/строка -> В чем проблема -> Техническое обоснование -> Как исправить (с примером кода).
    """

    # Colloect all request body together (Gemini clearly understand commands and data combinations)
    full_prompt = f"{system_prompt}\n\nВот изменения в Pull Request ({pr_title}), которые нужно проанализировать:\n\n{diff_content}"

    try:
        # Using tax-free and fast model gemini-2.5-flash
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": 0.1} # for code analysis always use 'temperature' 0.1 or 0.2 to prevent "fantasies"
        )
        response = model.generate_content(full_prompt)
        
        # Add sign to answer, for visibility in Git, about which AI model operated
        final_comment = f"🤖 **AI Reviewer** (Model: `{model_name}`)\n\n" + response.text
        with open("ai_response.md", "w", encoding="utf-8") as rf:
            rf.write(final_comment)
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

if __name__ == "__main__":
    main()