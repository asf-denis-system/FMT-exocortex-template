# IWE — Intellectual Work Environment

> Персональная среда для интеллектуальной работы и развития с ИИ-агентами.

Ты проходишь курсы. Бот помогает каждый день. Но знания остаются в голове, планы — в заметках, а контекст теряется между сессиями.

**IWE** — это интеллектуальная рабочая среда, где Claude помогает планировать неделю, фиксировать знания и строить собственную базу. Как IDE объединяет редактор, компилятор и дебаггер в одну среду для программиста — так IWE объединяет знания, планирование и ИИ-агентов в одну среду для мышления.

> **Ключевой принцип: экзоскелет, не протез.** IWE усиливает ваше мышление, а не заменяет его. После взаимодействия с IWE вы стали компетентнее, а не только получили результат.

---

## Как это выглядит на практике

- Утром — Стратег составил план ночью: уведомление в Telegram + файл DayPlan в репозитории
- Открываешь VS Code → `claude` → Claude знает, что в плане, и предлагает начать с приоритетного
- Работаешь — Claude фиксирует знания по ходу (Capture-to-Pack)
- Закрываешь сессию — результат зафиксирован, план обновлён
- В понедельник — Стратег готовит черновик недельного плана, вы обсуждаете его на сессии стратегирования

---

## Быстрый старт

### Требования

Два режима установки: **core** (минимальный, офлайн) и **full** (полный, с автоматизацией).

| Инструмент | Core | Full | Проверить | Установить |
|-----------|:----:|:----:|-----------|-----------|
| **ОС** | ✓ | ✓ | macOS, Linux, Windows (WSL) | — |
| **Git** | ✓ | ✓ | `git --version` | macOS: `xcode-select --install` / Linux: `sudo apt install git` |
| **AI CLI** | ✓ | ✓ | Любой: Claude Code, Codex, Aider и др. | См. [совместимость с AI CLI](#совместимость-с-ai-cli) |
| **VS Code** | ✓ | ✓ | `code --version` | [code.visualstudio.com](https://code.visualstudio.com) |
| GitHub CLI | — | ✓ | `gh --version` | macOS: `brew install gh` / Linux: [cli.github.com](https://cli.github.com/) |
| GitHub аккаунт | — | ✓ | `gh auth status` | `gh auth login` |
| Node.js | — | ✓ | `node --version` | Только если AI CLI = Claude Code |
| WakaTime | — | — | `wakatime-cli --version` | Опционально. `/setup-wakatime` в Claude Code |

> **Как открыть терминал:**
> - **macOS:** Spotlight (`Cmd + Space`) → наберите `Terminal` → Enter.
>   Или в VS Code: меню `Terminal` → `New Terminal` (`Ctrl + `` ` ``).
> - **Windows:** `Win + R` → наберите `cmd` → Enter. Рекомендуется: WSL (Windows Subsystem for Linux) для полной совместимости.
>   Или в VS Code: меню `Terminal` → `New Terminal` (`Ctrl + `` ` ``).
> - **Альтернатива:** Откройте VS Code, запустите Claude Code командой `claude` в терминале VS Code, и попросите его выполнить нужную команду.
>
> Далее все команды выполняются в терминале.

### Шаг 0: Создать рабочую папку

Создайте **одну папку** для всех репозиториев IWE. По умолчанию `~/IWE`:

```bash
mkdir -p ~/IWE
```

### Шаг 1: Клонировать и запустить установку

**Вариант A: Полная установка (~5 мин)** — git + GitHub + Claude Code + автоматизация Стратега:

```bash
cd ~/IWE
gh repo fork TserenTserenov/FMT-exocortex-template --clone --remote
cd FMT-exocortex-template
bash setup.sh
```

**Вариант B: Минимальная установка (~2 мин)** — только git, без сети, любой AI CLI:

```bash
cd ~/IWE
git clone https://github.com/TserenTserenov/FMT-exocortex-template.git
cd FMT-exocortex-template
bash setup.sh --core
```

Скрипт спросит:
- GitHub username (можно пропустить в core-режиме)
- Рабочую директорию (по умолчанию — родительская папка шаблона)
- Путь к Claude CLI и часовой пояс (только в полном режиме)

<details>
<summary>Что делает setup.sh</summary>

1. Проверяет prerequisites (git, gh, claude)
2. Показывает политику данных и запрашивает согласие ([DATA-POLICY.md](docs/DATA-POLICY.md))
3. Заменяет 7 плейсхолдеров (`{{GITHUB_USER}}`, `{{WORKSPACE_DIR}}` и др.)
4. Копирует `CLAUDE.md` → корень рабочей директории
5. Копирует `memory/*.md` → `~/.claude/projects/.../memory/`
6. Устанавливает launchd-агентов для Стратега
7. Создаёт `DS-strategy/` — приватный репозиторий для стратегирования

Посмотреть без выполнения: `bash setup.sh --dry-run`
</details>

<details>
<summary>Ручная настройка (если setup.sh не подходит)</summary>

1. Замените `{{GITHUB_USER}}` на ваш GitHub username во всех файлах
2. Замените `{{WORKSPACE_DIR}}` на путь к рабочей директории (напр. `~/IWE`)
3. Замените `{{HOME_DIR}}` на домашнюю директорию (значение `$HOME`)
4. Замените `{{CLAUDE_PROJECT_SLUG}}` на путь через дефисы (напр. для `~/IWE` → `-Users-yourname-IWE`)
5. Замените `{{TIMEZONE_HOUR}}` на час запуска стратега в UTC (напр. `4` для 7:00 MSK)
6. Замените `{{TIMEZONE_DESC}}` на описание времени (напр. `7:00 MSK`)
7. Замените `{{CLAUDE_PATH}}` на путь к Claude CLI (напр. `/opt/homebrew/bin/claude`)
8. Установите launchd-агентов: `cd roles/strategist && bash install.sh`
9. Скопируйте `memory/` в `~/.claude/projects/.../memory/`
10. Скопируйте `CLAUDE.md` в корень рабочей директории

</details>

### Шаг 2: Проверить установку

```bash
# Проверить файлы
ls ~/IWE/CLAUDE.md
ls ~/.claude/projects/*/memory/

# Проверить launchd (только macOS)
launchctl list | grep strategist

# Проверить DS-strategy
ls ~/IWE/DS-strategy/
```

### Шаг 3: Первая сессия (~30 мин)

```bash
cd ~/IWE
claude
```

Скажи Claude: **«Проведём первую стратегическую сессию»**

Claude прочитает CLAUDE.md и memory/ и проведёт тебя через:
1. **Определение целей** — Кем ты хочешь быть через год? Чему научиться?
2. **Неудовлетворённости** — Что мешает? Где разрыв между текущим и желаемым?
3. **Первый WeekPlan** — Конкретные задачи на неделю с бюджетами времени
4. **Обновление MEMORY.md** — Твои РП появятся в таблице

После этого Claude в каждой сессии будет видеть твой план и работать по нему.

---

## Обновления

Протоколы, промпты и справочники обновляются из upstream. Твои личные данные (планы, MEMORY.md, стратегия) **не затрагиваются**.

```bash
cd ~/IWE/FMT-exocortex-template
bash update.sh
```

| Команда | Что делает |
|---------|-----------|
| `bash update.sh` | Скачивает обновления из upstream, применяет к стандартным файлам |
| `bash update.sh --check` | Показать доступные обновления без применения |
| `bash update.sh --dry-run` | Показать что изменится, не применять |

**Что обновляется (standard):** CLAUDE.md, memory/*.md (кроме MEMORY.md), промпты Стратега.
**Что НЕ трогается (personal):** MEMORY.md (твои РП), DS-strategy/ (твои планы).

---

## Совместимость с AI CLI

Ядро IWE (CLAUDE.md, memory/, промпты) — это markdown-файлы. Они работают с **любым** AI CLI, который умеет читать файлы в рабочей директории.

| AI CLI | Интерактивная работа | Автоматизация (Стратег) | MCP-серверы | Примечание |
|--------|:-------------------:|:----------------------:|:-----------:|------------|
| **Claude Code** (рекомендуемый) | Полная | Полная | Да | Hooks, skills, settings. `npm install -g @anthropic-ai/claude-code` |
| **Codex** (OpenAI) | Работает | Через `AI_CLI=codex` | Нет | `npm install -g @openai/codex` |
| **Aider** | Работает | Через `AI_CLI=aider` | Нет | `pip install aider-chat`. Флаг: `AI_CLI_PROMPT_FLAG=--message` |
| **Continue.dev** | Работает | Нет | Частично | VS Code extension. Нет CLI для автоматизации |
| **Cursor** | Работает | Нет | Нет | Встроенный AI. Читает CLAUDE.md как project rules |

<details>
<summary>Как переключить AI CLI для автоматизации Стратега</summary>

```bash
# По умолчанию — Claude Code (ничего менять не нужно)
bash roles/strategist/scripts/strategist.sh morning

# Codex
AI_CLI=codex AI_CLI_PROMPT_FLAG=-p AI_CLI_EXTRA_FLAGS="" bash roles/strategist/scripts/strategist.sh morning

# Aider
AI_CLI=aider AI_CLI_PROMPT_FLAG=--message AI_CLI_EXTRA_FLAGS="" bash roles/strategist/scripts/strategist.sh morning
```

</details>

> **WakaTime** трекает время работы: по проектам, категориям, редакторам. Бесплатный план: статистика за 2 недели. **Настройка:** `/setup-wakatime` в Claude Code. Подробнее: [wakatime.com](https://wakatime.com).

> **Автоматизация Стратега:** на macOS — launchd (устанавливается автоматически). На Linux — cron (`crontab -e`). Без автоматизации — Стратег запускается вручную: `bash roles/strategist/scripts/strategist.sh morning`

---

## Документация

> **Первая установка?**
> [SETUP-GUIDE.md](docs/SETUP-GUIDE.md) — пошаговое руководство от чистого компьютера (30-60 мин).
>
> **Политика данных:**
> [DATA-POLICY.md](docs/DATA-POLICY.md) — какие данные собираются, где хранятся, как удалить.
>
> **Путь изучения:**
> [LEARNING-PATH.md](docs/LEARNING-PATH.md) — принципы, протоколы, агенты, Pack, SOTA.
>
> **Быстрая справка / FAQ:**
> [IWE-HELP.md](docs/IWE-HELP.md) — то же, что знает бот @aist_me_bot.
>
> **Почему принципы, а не навыки?**
> [principles-vs-skills.md](docs/principles-vs-skills.md) — аргументация и генеративная иерархия.

---

## Структура

```
FMT-exocortex-template/
│
├── CLAUDE.md                        # Правила для Claude Code (протоколы, архитектура)
├── README.md                        # Этот файл
├── REPO-TYPE.md                     # Тип репозитория (Format)
├── ONTOLOGY.md                      # Онтология IWE
├── update.sh                        # Обновление из upstream
│
├── memory/                          # Оперативная память (≤10 файлов, ≤100 строк каждый)
│   ├── MEMORY.md                    # ★ PERSONAL: задачи недели, навигация (авто-загрузка)
│   ├── protocol-open.md             # Протокол открытия сессии
│   ├── protocol-work.md             # Протокол работы
│   ├── protocol-close.md            # Протокол закрытия сессии
│   ├── navigation.md                # Навигация по репозиториям
│   ├── hard-distinctions.md         # Жёсткие различения
│   ├── fpf-reference.md             # Первые принципы (FPF)
│   ├── checklists.md                # Чеклисты
│   ├── sota-reference.md            # SOTA-практики
│   ├── repo-type-rules.md           # Правила по типам репозиториев
│   └── day-rhythm-config.yaml       # Ритм дня: помидорки, новости, стратег-день
│
├── docs/                            # Справочная документация
│   ├── SETUP-GUIDE.md               # Пошаговое руководство установки
│   ├── LEARNING-PATH.md             # Путь изучения IWE
│   ├── IWE-HELP.md                  # Справочник IWE для бота (FAQ, глоссарий)
│   ├── DATA-POLICY.md               # Политика данных IWE
│   ├── principles-vs-skills.md      # Почему принципы, а не навыки
│   └── adr/                         # Architecture Decision Records
│
├── roles/                           # Роли (точка расширения)
│   ├── strategist/                  # Роль: Стратег (R1)
│   │   ├── install.sh
│   │   ├── prompts/                 # 9 сценариев
│   │   └── scripts/                 # Скрипты запуска + launchd plist
│   ├── extractor/                   # Роль: Экстрактор знаний (R2)
│   └── synchronizer/                # Роль: Синхронизатор (R8)
│
├── setup/                           # Утилиты установки
│   ├── validate-template.sh         # Проверка плейсхолдеров
│   └── optional/                    # Опциональные компоненты
│       ├── README.md                # Документация (установка, настройка)
│       ├── pomodoro-alert.py        # Помодоро-напоминания (WakaTime + macOS)
│       └── pomodoro-alert.plist     # launchd агент для помодоро
│
├── seed/                            # Шаблоны → отдельные репо после setup
│   └── strategy/                    # → DS-strategy/ (стратегический хаб)
│
└── .claude/                         # Конфигурация Claude Code
    ├── settings.local.json          # MCP-серверы + разрешения
    ├── hooks/wakatime-heartbeat.sh  # WakaTime heartbeat
    └── skills/setup-wakatime.md     # /setup-wakatime
```

---

## FAQ

**Q: Нужна ли подписка Anthropic?**
A: Для полной установки (Claude Code) — да, рекомендуется **Claude Pro** ($20/мес). Для минимальной (`setup.sh --core`) — нет, работает с любым AI CLI.

**Q: Работает ли на Linux/Windows?**
A: Да. Ядро работает на любой ОС. Автоматизация Стратега: macOS — launchd (авто), Linux — cron (вручную), Windows — WSL + cron.

**Q: Что если я не хочу Стратега?**
A: Можно не устанавливать launchd-агентов. CLAUDE.md и memory/ будут работать и без них — просто не будет автоматических планов.

**Q: Как связан бот (@aist_me_bot) и IWE?**
A: Бот работает на тирах T1-T3 (без git). IWE (этот шаблон) — для T4+. Они используют одну базу знаний (через MCP-серверы), но IWE даёт больше: Claude Code, Стратег, свои Pack.

**Q: Что такое Pack?**
A: Pack — формализованная область знаний (паспорт предметной области). Pack — единственный source-of-truth для доменного знания. Подробнее: [LEARNING-PATH.md](docs/LEARNING-PATH.md).

**Q: Безопасны ли мои данные?**
A: Три зоны защиты: (1) **Локальная** — CLAUDE.md и memory/ на вашем компьютере; (2) **GitHub** — DS-strategy и Pack — приватные репозитории; (3) **Платформа** — per-user изоляция. Подробнее: [DATA-POLICY.md](docs/DATA-POLICY.md).

---

## Сокращения и термины

| Сокращение | Расшифровка |
|------------|-------------|
| **IWE** | Intellectual Work Environment — интеллектуальная рабочая среда |
| **ОС** | Операционная система (macOS, Linux, Windows) |
| **ОРЗ** | Открытие → Работа → Закрытие — три стадии каждой сессии |
| **РП** | Рабочий продукт — конкретный артефакт (документ, код, схема) |
| **WP** | Work Product — то же, что РП (англ.) |
| **Pack** | Паспорт предметной области — формализованные знания домена |
| **DS** | Delivery System — производная система (код, планы, публикации) |
| **FMT** | Format — шаблон структуры репозитория |
| **MCP** | Model Context Protocol — протокол доступа Claude к внешним данным |
| **FPF** | First Principles Framework — фреймворк первых принципов |
| **SPF** | Second Principles Framework — фреймворк вторых принципов (структура Pack) |
| **ZP** | Zero Principles — нулевые принципы (6 базовых ограничений) |
| **ЦД** | Цифровой двойник — модель пользователя в базе данных |
| **KE** | Knowledge Extraction — извлечение знаний из опыта в Pack |
| **UL** | Ubiquitous Language — единый язык предметной области (DDD) |
| **SOTA** | State Of The Art — лучшие современные практики |
| **AI CLI** | Командная строка ИИ-ассистента (Claude Code, Codex, Aider и др.) |
| **WSL** | Windows Subsystem for Linux — подсистема Linux в Windows |

---

## Лицензия

MIT
