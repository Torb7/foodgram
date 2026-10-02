# Foodgram

Foodgram — сервис публикации рецептов. Пользователи создают рецепты с
ингредиентами и тегами, подписываются на авторов, добавляют рецепты в
избранное и список покупок, а затем скачивают общий список ингредиентов.

Технический контракт API описан в
[OpenAPI-спецификации](docs/openapi-schema.yml).

## Возможности

- регистрация, аутентификация по токену и смена пароля;
- профили, аватары и подписки на авторов;
- создание, редактирование и удаление рецептов;
- теги, ингредиенты и поиск ингредиентов по началу названия;
- фильтрация рецептов, избранное и список покупок;
- скачивание списка покупок в формате TXT;
- короткие ссылки на рецепты.

## Стек

- Python 3.12;
- Django 5.2 и Django REST Framework 3.16;
- Djoser и django-filter;
- PostgreSQL 14;
- React 17;
- Docker, Docker Compose и nginx.

## Структура репозитория

```text
backend/              Django-проект и приложения api, recipes, users
frontend/             React-клиент
data/                 исходные данные ингредиентов
docs/                 OpenAPI-спецификация и страница ReDoc
infra/                отдельная конфигурация nginx для frontend и ReDoc
nginx/                nginx-образ для Docker-конфигураций в корне
postman_collection/   коллекция запросов Postman
```

## Локальный запуск API

Нужен Python 3.12 или совместимый с зависимостями Python 3.10+.
Текущая конфигурация Django для локального запуска использует SQLite.

```bash
git clone <URL-репозитория>
cd foodgram

python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

export DEBUG=True
python backend/manage.py migrate
python backend/manage.py load_ingredients
python backend/manage.py runserver
```

API станет доступен по адресу <http://127.0.0.1:8000/api/>.

`load_ingredients` загружает ингредиенты из
[`data/ingredients.json`](data/ingredients.json). Его следует выполнить после
миграций, чтобы поиск и создание рецептов могли использовать исходный набор
ингредиентов.

### Переменные окружения

Настройки Django читаются из окружения процесса. При прямом запуске файл
`.env` автоматически не загружается, поэтому переменные нужно экспортировать
в оболочке или передать через используемый инструмент запуска.

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `SECRET_KEY` | секретный ключ Django | новый случайный ключ на запуск |
| `DEBUG` | режим отладки | `False` |
| `ALLOWED_HOSTS` | допустимые хосты, через запятую | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | доверенные источники CSRF, через запятую | `http://localhost:8000` |

## API и дополнительные материалы

- OpenAPI: [`docs/openapi-schema.yml`](docs/openapi-schema.yml)
- ReDoc через `infra`: <http://localhost/api/docs/>
- Postman-коллекция:
  [`postman_collection/foodgram.postman_collection.json`](postman_collection/foodgram.postman_collection.json)

Основные маршруты:

| Маршрут | Назначение |
| --- | --- |
| `/api/auth/token/login/` | получить токен |
| `/api/users/` | пользователи и регистрация |
| `/api/users/subscriptions/` | подписки текущего пользователя |
| `/api/tags/` | теги |
| `/api/ingredients/` | ингредиенты и поиск |
| `/api/recipes/` | рецепты |

## Запуск ReDoc из `infra`

Этот способ предназначен для просмотра frontend-сборки и API-документации.
Он **не запускает Django API**: для API используйте инструкцию выше или
отдельную конфигурацию развёртывания.

Требуются Docker Engine и Docker Compose; порт `80` должен быть свободен.
Из корня репозитория выполните:

```bash
cd infra
docker compose up --build
```

Если используется устаревший отдельный бинарник Compose, команда аналогична:

```bash
docker-compose up --build
```

После сборки откройте <http://localhost/api/docs/>. Контейнер `frontend`
соберёт React-приложение и завершится — это ожидаемое поведение. Контейнер
nginx останется работать и будет раздавать ReDoc из папки `docs/`.

Чтобы остановить сервисы, нажмите `Ctrl+C`, затем выполните:

```bash
docker compose down
```

Страница ReDoc подключает JavaScript с CDN jsDelivr, поэтому браузеру нужен
доступ в интернет для её первого отображения.

## Тесты

Автоматические API-тесты написаны на `pytest` и находятся в
[`backend/tests/`](backend/tests/). Они проверяют:

- регистрацию, вход, выход и смену пароля;
- профили пользователей, аватары и подписки;
- получение и поиск ингредиентов, а также получение тегов;
- создание, просмотр, редактирование и удаление рецептов;
- валидацию обязательных полей и защиту от повторного добавления тегов,
  ингредиентов, избранного и списка покупок;
- фильтрацию, пагинацию, избранное и список покупок.

Чтобы запустить тесты из активированного виртуального окружения, выполните из
корня репозитория:

```bash
cd backend
pytest
```

## CI/CD

При каждом `push` в ветку `main` workflow
[`main.yml`](.github/workflows/main.yml) в GitHub Actions:

1. запускает проверку стиля `flake8` и API-тесты `pytest`;
2. собирает и публикует Docker-образы backend, frontend и nginx в Docker Hub;
3. развёртывает проект на удалённом сервере через
   `docker-compose.production.yml`, выполняет миграции и собирает статику.

Для работы workflow в репозитории должны быть настроены секреты GitHub:
`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `HOST`, `USER` и `SSH_KEY`.

## Автор

Проект выполнен в рамках курса **Яндекс Практикум**.

| Роль | GitHub |
|------|--------|
| Backend Developer | [Torb7](https://github.com/Torb7) |

## Адрес сайта: [edagram.sytes.net](https://edagram.sytes.net)
