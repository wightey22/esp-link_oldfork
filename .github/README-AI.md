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

---

Also I'm looked into another services/platforms which provides API access to their AI models on **"tier Free"** account basis (of cource with limits/restrictions, but most of them are sufficient to using on personal or not very complex development, etc).

Here is (provided data is actual on date of commiting this) some model plans provided by Groq API:
|Model                                    |RPM | RPD    | TPM | TPD      |	
|-----------------------------------------|----|--------|-----|----------|
|allam-2-7b                               |	30 |	7K    | 6K  |	500K	   |
|groq/compound                            |	30 |	250   | 70K | No limit |
|groq/compound-mini                       |	30 |	250	  | 70K | No limit |
|llama-3.1-8b-instant                     |	30 |	14.4K | 6K  | 500K	   |
|llama-3.3-70b-versatile                  | 30 |	1K	  | 12K | 100K	   |
|meta-llama/llama-4-scout-17b-16e-instruct|	30 |	1K	  | 30K | 500K	   |
|meta-llama/llama-prompt-guard-2-22m.     |	30 |	14.4K | 15K	| 500K	   |
|meta-llama/llama-prompt-guard-2-86m.     |	30 |	14.4K | 15K	| 500K	   |
|openai/gpt-oss-120b                      |	30 |	1K	  | 8K	| 200K	   |
|openai/gpt-oss-20b                       |	30 |	1K	  | 8K	| 200K	   |
|openai/gpt-oss-safeguard-20b             |	30 |	1K	  | 8K	| 200K	   |
|qwen/qwen3-32b                           |	60 |	1K	  | 6K	| 500K     |

---
</br>

From the **OpenAI** (ChatGPT models) on unpaid basis, as I figured out, we can use only as classic chat (since "OpenAI Platform" which provides API tokens avaliable only in paid tariffs), only possible useful option is connect *ChatGPT Codex Connector* to you GitHub account/workspace as external GitHub App to interact with your code repo from `https://chatgpt.com/apps/github/connector_{uuid}` app.

---
</br>

**Hugging Face Serverless Inference API** Lets you run open-source top models like Llama-3 or Qwen-2.5-Coder for free (with rate limits). However, it’s more difficult to configure code size/windows limits there. But anyway, really interesting variant for ones who are around AI-dev/AI-powered development porposes, entusiasts, etc.

---

Upd2: added manual-triggered AI-rewiever and comparser actions (analyser script `scripts/ai_manual_audit.py` and workflow definition `workflows/ai-manual-audit.yml`). It is runs on the most suitable model available for this purpose among those that are free-for-charge available - `gemini-3.5-flash`.  
To run go *Actions* tab, select *Manual AI Codebase Audit & Fork Compare*, hit Run workflow. If need to compare this repo with foreign fork, just type that fork repo-name as `{git_name/git_repo}` in the text filed. Else (when leaveing this field blank) the own repo will be rewieved/analysed. In both cases the report should be provided as auto-created *GitHub Issue* with all details in it.  
At least, the idea was exactly like that `¯\_(ツ)_/¯`

---

