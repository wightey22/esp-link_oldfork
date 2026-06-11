.github/workflows/ai-code-rewiever.yml - definition file for GitHub Workflow, sets the steps, triggers, data-collecting rules for AI API and calls the following function script

.github/scripts/ai_rewiev.py - just Python script with AI functions, there defining prompt for rewiev and AI model to call via API, initializing API and performing request.  
</br>
***
upd:

Main AI model changed to `gemini-3.5-flash`.  
Updated AI-script and wirkflow file - added model selector - basis on diffs amount and Pull Request header it will swich used models between `gemini-3.1-flash-lite` and `gemini-3.5-flash`. As example, if PR marked with one of `docs:`, `chore:`, `minor:` than lighter model will use for saving RequestPerDay quantity of main model.  
Updated AI "sysyem prompt" add bot specificates for better processing actual code stack, like development around MCU (ESP/RP2040), u-boot, etc.  
***  
</br>
Below are first/example versions of prompt text than defined in ai_rewiev.py:  
<details>
<summary>1st (click to wiev)</summary>
Ты — Senior Fullstack Engineer и System Architect с глубоким пониманием DevOps, низкоуровневой оптимизации и чистой архитектуры кода.
Твоя задача — провести жесткое, экспертное код-ревью предоставленного Git diff.

Сконцентрируйся на следующих аспектax:
1. **Критические ошибки и Баги**: Утечки памяти, race conditions, некорректная логика ветвления, граничные случаи (edge cases), отсутствие обработчиков ошибок (try/catch, проверка указателей).
2. **Оптимизация производительности**: Избыточные циклы, тяжелые аллокации памяти, неэффективные сетевые/IO операции.
3. **Добавление новых функций**: Если в PR реализуется новая фича, проверь, не забыл ли автор обновить конфигурации, сопутствующие методы, обработку флагов или документацию.
4. **Безопасность**: Уязвимости, захардкоженные секреты/токены.

Формат ответа: 
- Используй строгий Markdown. Пиши кратко, емко, без лишней вежливости и "воды".
- Ошибки и улучшения оформляй списком:
  - **Файл и строка**: Что не так.
  - **Почему это плохо**: Техническое обоснование.
  - **Как исправить**: Пример оптимизированного/исправленного кода в блоке кода.  
</details>  

<details>
<summary>2nd (click to wiev)</summary>  
Ты — Senior Fullstack Engineer и System Architect. Проведи экспертное код-ревью предоставленного Git diff.
Сконцентрируйся на критических багах, утечках памяти, оптимизации алгоритмов, чистом коде и безопасности.
    
Формат ответа:
- Используй строгий Markdown на русском языке.
- Пиши кратко и по делу.
- Ошибки оформляй списком: Файл/строка -> Что не так -> Как исправить (с примером исправленного кода).
</details></br>

---

A couple sutable for code rewiev purposes AI models I found available at Google AI Studio tax-free plan, of course with different limits of requests and tokens per periods (actual for *"Free tier"* tariff). Table below shows comparsions in  Model, RequestPerMinute, TokensPerMinute, RequestPerDay params. It seems, that these limits are actual for AI Studio project level, and applies per project, not per API-key.

| Model                          | RPM | TPM   | RPD  |
| ------------------------------ | --- | ----- | ---- |
| Gemini 2.5 Flash               | 5   | 250k  | 20   |
| Gemini 2.5 Flash Lite          | 10  | 250k  | 20   |
| Gemma 4 26B                    | 15  | unlim | 1.5k |
| Gemma 4 31B                    | 15  | unlim | 1.5k |
| Gemini 3.5 Flash               | 5   | 250k  | 20   |
| Gemini 3.1 Flash Lite          | 15  | 250k  | 500  |
| Gemini 3 Flash                 | 5   | 250k  | 20   |

Gemini by himself gives us the following usage recommendations:

- Gemini Flash (2.5 / 3 / 3.5) series - for complex tasks with strong context preservation (gemini-3.5-flash in table below)

- Flash Lite series - for simple commits and tests (gemini-3.1-flash-lite in table below)

- Gemma 4 (26B / 31B) - “Dark Horse”, open-weights model with a huge request limits and well-not-bad logic,
but small context window. May be very useful when dealing with frequent minor edits and syntax fixes.

Switching to using the another AI model can be made by changing param `model_name="{model_name}"` in ai_rewiev.py

**Pay your attention** when swithcing to Gemma models - their naming in script may be a little different, for example: `model_name="gemma-4-31b-it"`, where suffix "-it" means "instruction-tuned" (exactly what we need for rewiever).