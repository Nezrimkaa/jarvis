# 🤖 Jarvis Assistant

> **MVP** — Minimal Viable Product. Контекстный голосовой/текстовый ассистент для Windows.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## Возможности

Jarvis понимает сложные запросы в контексте диалога, а не по шаблонным командам:

```
Вы: создай файл test.txt
🤖 Готово

Вы: открой его
🤖 (понимает что "его" = test.txt)

Вы: создай на десктопе проект и открой в редакторе
🤖 (создаёт папку, файл, открывает редактор — цепочка действий)
```

### Команды и действия

| Категория | Что умеет |
|---|---|
| **Файлы** | создать, удалить, переместить, найти |
| **Папки** | создать, удалить |
| **Приложения** | открыть, закрыть |
| **Система** | громкость, скриншот, выключение, перезагрузка, сон, блокировка |
| **Браузер** | открыть URL, поиск, парсинг страниц, скриншоты |
| **Git** | коммит, пуш, пул, ветки, pull request |
| **Редактор** | открыть файл (VS Code / Notepad) |
| **Shell** | выполнить любую команду |
| **Код** | генерация через LLM |

### Интерфейс

- **Чат-окно** — пиши команды, получай ответы
- **Голосовой ввод** 🎤 — нажми кнопку, говори (Vosk, русский язык)
- **TTS** — ассистент отвечает голосом (Piper, русский язык)
- Трей-иконка для быстрого доступа

---

## Установка

```powershell
# 1. Клонировать
git clone https://github.com/Nezrimkaa/jarvis.git
cd jarvis

# 2. Установить зависимости
pip install -r requirements.txt
playwright install chromium

# 3. Настроить API ключи
# Создать .env на основе .env.example:
echo "GITHUB_TOKEN=ваш_github_token" > .env

# 4. Скачать модели (Vosk + Piper)
python -m jarvis.utils.download_models

# 5. Запустить
$env:PYTHONPATH = "src"
python -m jarvis
```

### Сборка .exe

```powershell
pip install pyinstaller
pyinstaller jarvis.spec
# .exe в dist/jarvis.exe
```

---

## Технологии

| Компонент | Технология |
|---|---|
| **LLM (NLU)** | [GitHub Models API](https://github.com/marketplace/models) (GPT-4o-mini, бесплатно) |
| **ASR (речь в текст)** | [Vosk](https://alphacephei.com/vosk/) (русская модель, локально) |
| **TTS (текст в речь)** | [Piper](https://github.com/rhasspy/piper) (русский голос, локально) |
| **OS-автоматизация** | `pywinauto`, `PyAutoGUI`, PowerShell |
| **Браузер** | [Playwright](https://playwright.dev) (Chromium) |
| **Git** | GitPython + PyGitHub |
| **GUI** | `tkinter` (чат) + `pystray` (трей) |

### Провайдеры LLM

Используется **GitHub Models** (бесплатно, нужен GitHub токен из .env). Достаточно 5 USD кредитов Azure — GPT-4o-mini очень дешёвый.

---

## Архитектура

```
src/jarvis/
├── core/           # конфиг, сессия, точка входа
├── nlu/            # LLM-клиент, контекстный парсер
├── actions/        # диспетчер + исполнители (файлы, ОС, браузер, Git...)
├── audio/          # Vosk STT + Piper TTS
├── activation/     # хоткей (Ctrl+Win+Z)
├── ui/             # чат-окно + трей
└── utils/          # логирование, безопасность, скачивание моделей
```

### Как это работает

```
[user text] + [история диалога] + [контекст (путь, десктоп, username)]
    → LLM (GitHub Models)
        → либо текст (диалог)
        → либо [ACTION] цепочка действий
    → ActionDispatcher.execute_plan()
    → ответ пользователю
```

---

## Разработка

```powershell
# TDD — все тесты
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
```

---

## Лицензия

MIT. Сделано для себя, но может быть полезно кому-то ещё.
