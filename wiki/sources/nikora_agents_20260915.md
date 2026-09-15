# NIKORA: источники агентного плана, 15.09.2026

Синтез: [[roadmap/nikora_agent_delivery_plan]], [[runbooks/nikora_agent_launch]], [41 карточка](../requirements/nikora_sprints/index.md). Числа — расчётная гипотеза до S0, не коммерческое предложение и не результаты исполнения спринтов.

## Задача и состояние оборудования

Владелец запросил законченные проверяемые спринты, отдельные архитектуру/функциональность, распределение GPT/Claude/local и оценку tokens/USD/time. Последние уточнения имеют приоритет: **сервер уже куплен и находится у владельца, но ещё не запущен; доступны две карты по 16 ГБ. Учитывать только электричество и время владельца, без амортизации.** Облачные API считаются отдельно; человеческие часы не переведены в доллары.

Прошлые формулировки «сервера нет» и вариант с условной ценой владения отменены. Мощность 0,8 kW и тариф $0,10/kWh — подставляемые допущения, не измерения. Реальную доступную память, SKU, топологию и питание проверяет S0. Расхождение с [официальной спецификацией A100 40/80 GB](https://www.nvidia.com/en-us/data-center/a100/) записано, но план не подменяет заявленные 2 × 16 ГБ.

## Основания проекта

- [[requirements/nikora_gap_analysis_20260915]] и [[sources/nikora_20260915]]: актуальные постановки, ограниченные probes кода и неопределённости.
- [[architecture/nikora_minimal_extension]]: не заменять WMS и не заводить параллельный stock ledger.
- [[roadmap/nikora_ui_subsprints]]: 23 родительских функциональных инкремента.
- [[requirements/nikora_ui_workplaces_tz]], [[requirements/nikora_ui_quality_tz]], [[requirements/nikora_ui_reachtruck_tz]], [[requirements/nikora_ui_reachtruck_dispatch_tz]]: рабочие места и физические критерии приёмки.
- Проверяемые пути расширения указаны в каждой карточке; будущие тесты явно обозначены как будущие. Текущие незакоммиченные изменения пользователя не менялись этой задачей.

## OpenAI: официальный каталог и установка

Проверены [каталог](https://developers.openai.com/api/docs/models) и [цены API](https://developers.openai.com/api/docs/pricing), страницы [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra). Точные цены input/cache-read/cache-write/output сохранены в [budget.json](../../wiki-raw/nikora_agent_plan_20260915/budget.json).

API Standard, не Fast. Промо-цена Sol указана как минимум до 21.11.2026; пересматривать каждый спринт. Model ID из каталога не гарантирует доступность в аккаунте. GPT-5.7 в проверенном каталоге не подтверждён; «Astro» сопоставлен Astra как рабочая интерпретация, не как отдельный продукт.

[Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): установка, модель, effort и локальный provider. Дополнительно прочитаны локальные codex --version / codex exec --help: 0.154.0-alpha.6.2; проверены -m/-C/-s/--json/--oss/--local-provider. Отдельный денежный limit в этом exec help не найден; текстовый бюджет не объявлен жёстким ограничителем.

## Anthropic: цены, версии, ограничения CLI

- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing), [model overview](https://platform.claude.com/docs/en/models/overview).
- [Sonnet 5 announcement, поправка от 10 августа](https://www.anthropic.com/news/claude-sonnet-5): старое плановое повышение $3/$15 отменено; для расчёта взята действующая цена $2/$10. Не смешивать старый поисковый сниппет с текущей таблицей.
- [CLI reference](https://code.claude.com/docs/en/cli-reference): --max-budget-usd и --max-turns относятся к print mode; учёт subagents/остановка background workers в cap требуют актуальной версии (в документации ≥2.1.217). allowedTools — не полная изоляция ОС.
- [Setup](https://code.claude.com/docs/en/setup), [model config](https://code.claude.com/docs/en/model-config): установка, версии и effort.
- Claude Code — оболочка, не название модели. Подписка и API не складываются автоматически за одинаковое использование.

## Локальные кандидаты и память

- [Qwen2.5-Coder-14B GGUF от Qwen](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF), [Ollama 14B](https://ollama.com/library/qwen2.5-coder:14b): кандидат Q4 около 9 GB весов на одну 16 GB карту, далее нужен KV/runtime запас.
- [Qwen3-Coder-30B-A3B от Qwen](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct), [Ollama tags](https://ollama.com/library/qwen3-coder/tags): Q4 около 19 GB весов; обе карты для одной модели. Активные 3,3B MoE не означают, что все веса помещаются как 3,3B.
- [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) — дополнительный кандидат для отдельного benchmark, не основание обещать лучший результат на данном коде.
- [Ollama FAQ](https://docs.ollama.com/faq), [GPU](https://docs.ollama.com/gpu), [context length](https://docs.ollama.com/context-length): parallelism увеличивает память; multi-GPU не превращает две карты в один монолитный VRAM. Для coding agents рекомендуется 64k, поэтому ограниченный Aider ticket на 16/32k — базовый вариант, а полный Codex/Claude local — только после отдельной квалификации.
- [Linux install](https://docs.ollama.com/linux), [Modelfile](https://docs.ollama.com/modelfile), [Claude integration](https://docs.ollama.com/integrations/claude-code), [Codex integration](https://docs.ollama.com/integrations/codex).
- [Aider install](https://aider.chat/docs/install.html), [Ollama](https://aider.chat/docs/llms/ollama.html), [options](https://aider.chat/docs/config/options.html): uv, ollama_chat provider, model settings, scope/context и отключение автоматических commits.

Скорость, OOM, accepted-task rate и стоимость ошибок не измерены. Новизна модели не равна квалификации на legacy Oracle/WMS. Нет разрешённого автоматического fallback из локальной модели в облако с реальными данными.

## Что проверено этим планированием

- Локально обнаружен Ollama 0.33.1; claude/uv/aider не найдены через Get-Command. Это текущая Windows-среда, не инвентаризация ещё не запущенного сервера.
- Подготовлены 41 карточка, общий договор, шаблоны, команды запуска, расчёт и его локальная проверка.
- Проверка [check_budget.py](../../wiki-raw/nikora_agent_plan_20260915/check_budget.py): арифметика, зависимости, календарь, ссылки и согласованность карточек с таблицей. Успех этого скрипта не доказывает реализованный функционал.
- Не проводились установка сервера, загрузка весов, оплачиваемые model calls, production/Oracle mutations, Git push или публикация новых документов на Drive.

