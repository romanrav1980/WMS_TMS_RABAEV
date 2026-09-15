# NIKORA: установка и ограниченный запуск агентов

Дата: 15.09.2026. Сервер уже куплен и находится у владельца, но ещё не запущен; **установка и модели на этом сервере пока не проверены**. Ниже инструкция первого запуска и отдельных worktree, не отчёт о выполненной установке. В текущей Windows-среде обнаружены Codex CLI 0.154.0-alpha.6.2 и Ollama 0.33.1; claude/uv/aider не найдены через Get-Command (это не полный аудит установки и не инвентаризация GPU-сервера).

Связь: [[roadmap/nikora_agent_delivery_plan]], [[requirements/nikora_sprint_contract]], [карточки](../requirements/nikora_sprints/index.md). Конкретная модель/роль указана в §5 каждой карточки.

## 1. Рекомендуемый минимальный набор

- **Облако:** Codex CLI + GPT-5.6 Terra/Sol и GPT-6 Astra; Claude Code + Claude Sonnet 5/Opus 5. Доступ зависит от аккаунта/оплаты. GPT-5.7 не использовать как выдуманный ID.
- **Локально:** Ollama как inference server, **Aider** как ограниченный редактор небольшого набора файлов. Основная пара для 2 × 16 GB — Qwen2.5-Coder-14B Q4 и Qwen3-Coder-30B-A3B Q4 как два альтернативных режима.
- **Тесты:** имеющиеся pytest/Playwright/Oracle runner. Не тратить LLM на повторное «ручное» исполнение того, что проверяет CI.
- Не добавлять одновременно vLLM, OpenHands, ещё один orchestrator и fine-tuning. Если базовый контур не проходит S0, сначала выяснить причину, а не строить агентную платформу.

Выбор Qwen не означает доказанного превосходства над всеми новыми моделями. Это проверяемый baseline для небольших patches; [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) можно добавить кандидатом S0 при наличии поддерживаемого quant/runtime, но не подменять базовый профиль без замера.

## 2. Первый запуск уже купленного GPU-сервера

Пользователь подтвердил две карты с 16 GB каждой. До установки проверить физический SKU, не по надписи продавца:

```bash
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv
nvidia-smi -L
nvidia-smi topo -m
```

Официальный [A100 имеет 40/80 GB](https://www.nvidia.com/en-us/data-center/a100/); возможное другое устройство/ограничение ресурса нужно выяснить, не предполагая большой объём памяти. Проверить также поддерживаемую архитектуру CUDA/Flash Attention, охлаждение/питание и доступность обеих GPU одному процессу. NVLink не предполагается.

Рекомендация к конфигурации, не требование модели: Linux x86-64, 64 GB RAM минимум для комфортной работы системы/двух моделей, предпочтительно 128 GB при нескольких рабочих копиях; NVMe с запасом не менее 100 GB под модели/кэш/артефакты. CPU offload допускается только как явно измеренное ухудшение, не «GPU работает нормально».

## 3. Установка inference и Aider

Официальные инструкции: [Ollama Linux](https://docs.ollama.com/linux), [аппаратная совместимость](https://docs.ollama.com/gpu), [Aider installation](https://aider.chat/docs/install.html).

На новом выделенном Linux-хосте после проверки официального install script:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
python -m pip install uv
uv tool install --python python3.12 --with pip aider-chat
aider --version
```

Это примеры команд для администратора, они в текущей задаче не выполнялись. После S0 зафиксировать версии CLI и digest моделей; не обновлять runtime посередине приёмки. Не устанавливать пакеты Aider в venv WMS.

### Режим L1: две независимые небольшие копии

[Qwen2.5-Coder:14b](https://ollama.com/library/qwen2.5-coder:14b) — Q4_K_M, около 9 GB весов. Контекст/runtime требуют дополнительную память.

На выделенном сервере не запускать manual instance поверх уже слушающего те же порты системного сервиса. После согласованной остановки его администратором — два терминала/две systemd-службы:

```bash
# Терминал 1 / GPU 0
CUDA_VISIBLE_DEVICES=0 OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=16384 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_MAX_QUEUE=2 ollama serve
```

```bash
# Терминал 2 / GPU 1
CUDA_VISIBLE_DEVICES=1 OLLAMA_HOST=127.0.0.1:11435 OLLAMA_CONTEXT_LENGTH=16384 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_MAX_QUEUE=2 ollama serve
```

В отдельном управляющем терминале:

```bash
OLLAMA_HOST=127.0.0.1:11434 ollama pull qwen2.5-coder:14b
OLLAMA_HOST=127.0.0.1:11434 ollama show qwen2.5-coder:14b
OLLAMA_HOST=127.0.0.1:11434 ollama ps
```

Если экземпляры используют разные хранилища моделей, загрузить тот же digest и на второй. Не запускать параллельные pull в общее хранилище без необходимости. После реального запроса проверить PROCESSOR/CONTEXT в ollama ps и VRAM каждой карты.

В S0 протестировать OLLAMA_FLASH_ATTENTION=1 + OLLAMA_KV_CACHE_TYPE=q8_0, **только если backend/GPU поддерживают**. При unsupported/OOM убрать принудительное включение, снизить контекст до 8k и уменьшить входной пакет до 4–5k, либо выбрать меньшую модель. Не игнорировать silent truncation/CPU offload.

### Режим L2: одна более крупная модель на обеих GPU

Остановить два L1 instance после завершения их задач; нельзя одновременно ожидать память для обоих режимов. [Qwen3-Coder 30B Q4](https://ollama.com/library/qwen3-coder/tags) занимает около 19 GB только весами. MoE 3,3B активных параметров не означает 3,3B хранимых весов.

```bash
CUDA_VISIBLE_DEVICES=0,1 OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=32768 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_MAX_QUEUE=2 ollama serve
```

```bash
OLLAMA_HOST=127.0.0.1:11434 ollama pull qwen3-coder:30b-a3b-q4_K_M
OLLAMA_HOST=127.0.0.1:11434 ollama ps
```

[Ollama распределяет не помещающуюся модель между GPU](https://docs.ollama.com/faq), но headroom/скорость зависят от устройства, межсоединения, KV cache и контекста. Старт — 32k, один запрос; не выставлять 256k из карточки модели на 32 GB суммарно.

## 4. Безопасный удалённый доступ

Inference слушает только localhost на сервере. Не открывать 11434 в Интернет без аутентификации/TLS. Для рабочего компьютера — SSH tunnel:

```bash
ssh -N -L 11434:127.0.0.1:11434 -L 11435:127.0.0.1:11435 user@GPU_SERVER
```

Если локальный Ollama уже занимает 11434, выбрать свободные локальные порты, например 21434/21435, и поменять OLLAMA_API_BASE. Не останавливать чужой сервис ради примера. В Windows запускать туннель штатным OpenSSH, не раскрывая пароль в командной строке.

API-совместимость не является sandbox: worker должен видеть только task bundle/worktree, без пользовательского home, production DSN и ключей cloud/ERP. После начальной загрузки моделей ограничить исходящую сеть. Модели с суффиксом :cloud — **не локальные**.

## 5. Ограниченный local worker через Aider

Координатор сначала читает AGENTS.md/wiki, выбирает карточку и формирует обезличенный task bundle: approved context, 1–3 редактируемых файла, нужные интерфейсы read-only и независимые тестовые ожидания. Маленькая модель не должна получать весь проект/wiki/history в 16k контекст.

Для L1 вход, включая инструкции/файлы, ≤8–10k tokens, ответ ≤4k, запас на служебный контекст. L2 — вход ≤20–24k, ответ ≤4k в контексте 32k. Если пакет не помещается, его разбивает координатор, а не молча обрезает backend.

Пример отдельного .aider.model.settings.yml в task bundle:

```yaml
- name: ollama_chat/qwen2.5-coder:14b
  edit_format: diff
  extra_params:
    temperature: 0.1
    num_ctx: 16384
    num_predict: 4096
- name: ollama_chat/qwen3-coder:30b-a3b-q4_K_M
  edit_format: diff
  extra_params:
    temperature: 0.1
    num_ctx: 32768
    num_predict: 4096
```

Это стартовые параметры для маленького diff, не универсальный optimum Qwen. Фиксированный num_ctx нужен, потому что [Aider иначе подбирает окно динамически](https://aider.chat/docs/llms/ollama.html).

```bash
export OLLAMA_API_BASE=http://127.0.0.1:11434
aider --model ollama_chat/qwen2.5-coder:14b --model-settings-file .aider.model.settings.yml --map-tokens 512 --max-chat-history-tokens 2048 --no-auto-commits --no-dirty-commits --no-auto-test --no-auto-lint --no-suggest-shell-commands --analytics-disable --message-file TASK.md --read CONTEXT.md module.py test_module.py
```

TASK.md/CONTEXT.md/module.py — **заменяемые примеры**, координатор задаёт реальные файлы конкретного ticket; не запускать эту строку вслепую в корне проекта. Aider обрабатывает одно сообщение и выходит; не более двух повторов. Его file list и prompt не являются защитой ОС: запускать в изолированном bundle/контейнере без секретов. Тестовый runner отдельно проверяет patch; перенос в worktree только после scope check.

Для второй GPU использовать endpoint 11435. Для L2 поменять model ID на qwen3-coder:30b-a3b-q4_K_M и не запускать второго worker одновременно. Параметры CLI проверены по [Aider options](https://aider.chat/docs/config/options.html).

## 6. Облачный Codex

Официально: [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [config reference](https://learn.chatgpt.com/docs/config-file/config-reference). В текущей среде read-only проверены codex --version и codex exec --help; доступны -m, -C, -s, --json, --oss и --local-provider. Отдельного флага денежного лимита в проверенном exec help **нет**.

Установка на рабочем компьютере с поддерживаемым Node/npm:

```powershell
npm install -g @openai/codex
codex --version
codex login
```

ChatGPT login расходует allowance подписки; API-ключ — API billing. Ключ получать/хранить безопасно, не вставлять в ТЗ/командную строку/репозиторий. При первом реальном API-запуске согласовать аккаунт/проект и бюджет.

Один готовый ticket в отдельном worktree:

```powershell
codex exec -C C:/work/nikora-ticket -m gpt-5.6-sol -c 'model_reasoning_effort="high"' -s workspace-write --json "Прочитай AGENTS.md, wiki/index.md и TASK.md. Выполни только указанный ticket. Не делай commit/push/deploy. Верни diff, тесты и остаточные риски."
```

Для Terra менять -m gpt-5.6-terra и effort medium; для критического X — gpt-6-astra/high. Инструкции repo и текущие права сохраняются. Не использовать danger-full-access, bypass approvals или произвольные сетевые MCP для экономии времени.

Standard processing; проверить, не унаследован ли Fast из конфигурации. Контекст на новый ticket 16–32k, для сложного ≤64k; это организационный лимит контекст-пакета, не выдуманный CLI-флаг. output limits/usage уточняются возможностями установленной версии. Не требовать temperature от reasoning-модели как универсальный параметр.

Денежный контроль Codex: короткая сессия, токенный бюджет в TASK как **мягкое** условие, usage JSON и внешняя проверка после каждой сессии; hard cutoff нужен на утверждённом gateway/runner, если он требуется. Порог в тексте промпта и billing alert не гарантируют жёсткий stop. Не обещать флаг --max-budget-usd для Codex.

## 7. Claude Code: реализация и независимые тесты

Официально: [установка](https://code.claude.com/docs/en/setup), [CLI](https://code.claude.com/docs/en/cli-reference). Windows:

```powershell
winget install Anthropic.ClaudeCode
claude --version
claude
```

Выполнить вход штатным интерфейсом; не передавать ключ в текст задачи. Запуск одного ticket в выбранном worktree:

```powershell
claude -p --model claude-sonnet-5 --effort medium --max-turns 25 --max-budget-usd 8 --output-format json "Прочитай AGENTS.md, wiki/index.md и TASK.md. Реализуй только этот ticket и его тесты, без commit/push/deploy."
```

Для независимого критического теста:

```powershell
claude -p --model claude-opus-5 --effort high --max-turns 25 --max-budget-usd 15 --output-format json "Прочитай TASK.md и patch. Проверь контракт независимо. Production-код не менять; новые тесты только в разрешённом test worktree. Найди негативные и конкурентные случаи."
```

Это лимиты **одной сессии**, не всего спринта. В карточке бюджет шире, но каждая следующая сессия учитывает остаток. --max-budget-usd/--max-turns относятся к print mode; серверный/финансовый учёт всё равно сверять. По текущей документации для учёта subagents в cap и остановки background workers нужна Claude Code ≥2.1.217. Не включать subagents без необходимости; один review run дешевле бесконтрольного дерева.

Не использовать --dangerously-skip-permissions. --allowedTools задаёт действия без запроса, а **не** строгий список всех доступных инструментов; для ограничения смотреть --tools/--disallowedTools и OS sandbox. Готовые тесты запускать разрешённым runner, а не выдавать модели полный shell с production credentials.

## 8. Codex/Claude Code поверх локальной Qwen — опционально

Это возможно, но не базовый профиль L1: интеграции [Claude Code](https://docs.ollama.com/integrations/claude-code) и [Codex](https://docs.ollama.com/integrations/codex) рекомендуют **не менее 64k контекста**. На 2 × 16 GB сначала проверить L2 при 64k и один slot; если память/качество не позволяют, остаться на Aider с коротким bundle.

После успешной отдельной квалификации:

```bash
ollama launch claude --model qwen3-coder:30b-a3b-q4_K_M
```

Либо поддерживаемая локальная ветка Codex:

```bash
codex exec --oss --local-provider ollama -m qwen3-coder:30b-a3b-q4_K_M -s workspace-write "Выполни только утверждённый TASK.md"
```

Совместимость protocol/tool calling и реальный контекст проверяются S0, наличие флага не доказывает качества. Не настраивать cloud fallback незаметно: иначе локальные задания начнут стоить денег/выгружать код.

## 9. Параметры и остановки по классам

| Класс | Контекст входного пакета | Изменения | Один запуск | После двух неудач |
|---|---|---|---|---|
| L1 | 8–10k, окно 16k | 1–3 файла / ~250 строк | 1 Aider request, ≤4k output | L2 или C |
| L2 | 20–24k, окно 32k | 1–4 файла / один контракт | 1 request, ≤4k output | C/H |
| C / Terra review | 16–32k | 3–6 файлов / один сценарий | 20–25 turns; Claude $5–8 | H |
| H | 32–64k | один инвариант / обычно ≤8 файлов | 25–30 turns; Claude $10–15, Codex внешний usage control | X |
| X | ≤64k | только сложное ядро + тестовый oracle | короткие сессии, ~30 turns; budget из карточки | Человек / пересмотр ТЗ |

Turn limit не равен времени или токенам. Не задавать всем max reasoning, миллионный контекст и полное дерево репозитория. Использовать стабильный короткий prefix для caching; не вешать keepalive вызовы ради абстрактного hit-rate.

## 10. Шаблоны и отчётность

[Шаблон ticket](../../wiki-raw/nikora_agent_plan_20260915/task.template.md), [шаблон независимой проверки](../../wiki-raw/nikora_agent_plan_20260915/review.template.md). Заполнять до запуска: исходная ревизия, список файлов, точные критерии, команды тестов, ограничение бюджета и stop rules.

Usage: input/cache-write/cache-read/output, model ID, effort, retry count, accepted/rejected, engineer review minutes. Считать стоимость принятого патча и latency, не только tokens/s. Если локальная модель требует больше исправлений, чем Luna/Sonnet, назначение локально меняется после evidence, даже если API у неё бесплатен.

Работа этого документа — рекомендация настройки. Реальной установки, загрузки весов, измерения GPU, покупки сервера, запуска оплачиваемых агентов и применения миграций в этой задаче не было.
