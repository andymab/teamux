# Teamux — AI‑инструмент для SMM (Groq + Stability + Telegram)

## 🚀 Обзор

**Teamux** — это контейнеризированное веб‑приложение, объединяющее Vue 3 + Vuetify 3 (фронтенд) и FastAPI (бекенд). Проект предназначен для SMM‑специалистов и маркетологов, которым требуется быстро анализировать статьи, генерировать визуалы и публиковать результаты в Telegram.

### Возможности

* 🔍 Анализ текста или HTML‑страницы по ссылке через **Groq API** (аналог OpenAI ChatCompletions).
* 🧠 Выжимка по основным пунктам (идея, ключевые тезисы, польза, аудитория).
* 🎨 Генерация картинки по английскому промпту через **Stability AI** (Stable Image Ultra).
* 📣 Автоматическая публикация текста и изображения в Telegram.
* 🔐 Защита API токеном и гибкая настройка окружения через `.env`.

---

## 📁 Структура проекта

```
teamux/
├─ docker-compose.yml
├─ Makefile
├─ .env.example
├─ .gitignore
├─ api/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ app/
│     ├─ main.py # FastAPI-приложение и роуты
│     ├─ deps.py # CORS, проверка токена
│     ├─ groq_client.py # Анализ текста через Groq API
│     ├─ post_builder.py # Генерация постов из шаблонов (Groq)
│     ├─ fetcher.py # Загрузка и очистка HTML-статей
│     ├─ stability.py # Генерация изображений через Stability
│     ├─ telegram.py # Публикация постов в Telegram
│     └─ templates/
│     └─ prompt_tg_post_ru.txt # Шаблон промпта для поста
└─ web/
   ├─ Dockerfile
   ├─ index.html
   ├─ package.json
   ├─ vite.config.ts
   └─ src/
      ├─ main.ts              # Точка входа Vue + Vuetify
      ├─ App.vue              # Основной интерфейс SMM‑панели
      └─ api.ts               # Клиент для обращения к FastAPI
```

---

## ⚙️ Быстрый старт

```bash
git clone https://github.com/yourname/teamux.git
cd teamux
cp .env.example .env
# впишите свои ключи GROQ, Stability, Telegram
make up      # собрать и запустить контейнеры
echo "Открой http://localhost:5173"
```

---

## 🧱 Основные контейнеры

| Сервис  | Порт | Назначение                                 |
| :------ | :--- | :----------------------------------------- |
| **api** | 8000 | FastAPI‑бэкенд (Groq, Stability, Telegram) |
| **web** | 5173 | Vite + Vue 3 интерфейс                     |

---

## 🧩 Makefile команды

```makefile
make up           # сборка и запуск контейнеров
make down         # остановка и удаление
make restart      # пересборка и перезапуск
make logs         # общие логи
make api-logs     # логи бекенда
make web-logs     # логи фронтенда
make api-shell    # терминал внутри api
make web-shell    # терминал внутри web
make curl-analyze # тест запроса /analyze
make image        # тест генерации картинки
```

---

## 🔐 Пример `.env`

```env
# API keys
GROQ_API_KEY=your_groq_key
STABILITY_API_KEY=your_stability_key
TELEGRAM_BOT_TOKEN=123456:ABC-XYZ
TELEGRAM_CHAT_ID=@your_channel

# API config
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Web config
VITE_API_TOKEN=supersecret
```

---

## 🧠 Использование

1. В интерфейсе введи **текст** или **ссылку** на статью.
2. Выбери модель Groq (по умолчанию `llama-3.3-70b-versatile`).
3. Нажми **«Анализировать»** или **«Получить и проанализировать»**.
4. После анализа:

   * можно **опубликовать** результат в Telegram;
   * при необходимости сгенерировать **EN‑промпт** и отправить картинку.

---

## 🧰 Разработка и отладка

* **web-shell** — запустить интерактивно и руками выполнить `npm run dev` для горячей перезагрузки.
* При занятости порта 5173 Vite автоматически переключится на 5174 (см. логи `make web-logs`).
* Для детерминированного порта добавлен флаг `--strictPort`.
* Если проект монтируется в volume, node_modules маппится как `/app/node_modules` чтобы не затирать зависимости.

---

## 🧾 Лицензия и автор

MIT © 2025 Andy Minaev Teamux Dev Group
