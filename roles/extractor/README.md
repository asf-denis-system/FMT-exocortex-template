# Экстрактор (Knowledge Extractor, R2)

> Извлекает, формализует и маршрутизирует знания в Pack-репозитории.

## Что делает

При закрытии сессии или по запросу — находит знания (паттерны, различения, методы, ошибки), формализует по шаблону SPF и предлагает записать в правильный Pack. Пользователь всегда одобряет перед записью.

## Сценарии

| Сценарий | Триггер | Режим |
|----------|---------|-------|
| **Session-Close** | Закрытие сессии (протокол Close) | Интерактивный |
| **On-Demand** | «Запиши это в Pack» | Интерактивный |
| **Knowledge Audit** | «Аудит Pack» / ежемесячно | Интерактивный |
| **Inbox-Check** | launchd каждые 3ч (опционально) | Headless (отчёт) |

## Когда подключать

- Создал первый Pack (PACK-{твоя-область})
- Работаешь с Claude Code регулярно (≥3 сессии/неделю)
- Хочешь автоматически фиксировать знания

## Установка

### 1. Настрой маршрутизацию

Отредактируй `config/routing.md` — добавь свои Pack'и:

```markdown
| Домен | Pack | Префикс | Путь |
|-------|------|---------|------|
| Мой домен | PACK-my-domain | MD | c:/Users/Денис/projects/github/PACK-my-domain/pack/my-domain/ |
```

### 2. (Опционально) Установи автоматический inbox-check

```bash
cd c:/Users/Денис/projects/github/FMT-exocortex-template/roles/extractor
bash install.sh
```

Это установит launchd-агент для проверки inbox каждые 3 часа.

### 3. Ручной запуск

```bash
# Inbox-check (без launchd)
bash c:/Users/Денис/projects/github/FMT-exocortex-template/roles/extractor/scripts/extractor.sh inbox-check

# Knowledge Audit
bash c:/Users/Денис/projects/github/FMT-exocortex-template/roles/extractor/scripts/extractor.sh audit
```

## Как работает

```
Capture-to-Pack Pipeline:

  Обнаружение → Классификация → Маршрутизация → Формализация → Валидация → Одобрение → Запись

  1. Найти знания (captures + пропущенные инсайты)
  2. Определить тип (entity, distinction, method, fm, wp, rule)
  3. Определить Pack по домену (routing.md)
  4. Создать файл по шаблону SPF (ID, frontmatter, секции)
  5. Проверить: нет ли дубликатов и противоречий
  6. Показать Extraction Report пользователю
  7. Записать только одобренное
```

## Файлы

| Файл | Назначение |
|------|-----------|
| `config/routing.md` | Таблицы маршрутизации (Pack'и, типы, директории) |
| `config/feedback-log.md` | Лог отклонённых кандидатов (не предлагать повторно) |
| `prompts/session-close.md` | Промпт: экстракция при закрытии сессии |
| `prompts/on-demand.md` | Промпт: экстракция по запросу |
| `prompts/inbox-check.md` | Промпт: headless проверка inbox |
| `prompts/knowledge-audit.md` | Промпт: аудит Pack'ов |
| `scripts/extractor.sh` | Скрипт запуска (аналог strategist.sh) |
| `scripts/launchd/` | launchd plist для inbox-check |

## Принципы

1. **Human-in-the-loop:** Экстрактор предлагает, не записывает без одобрения
2. **Один пайплайн:** Все сценарии используют classify → route → formalize → validate
3. **Тест универсальности:** Можно использовать в другом контексте? Нет → governance, не экстрагируй
4. **Lazy reading:** Inbox-check читает только целевой Pack, не все сразу

---

*Source-of-truth: DP.AISYS.013 (PACK-digital-platform)*
