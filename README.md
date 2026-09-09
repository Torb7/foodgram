# Foodgram

Foodgram — сервис для публикации рецептов. Пользователи могут создавать и
редактировать рецепты, подписываться на авторов, добавлять рецепты в избранное
и список покупок, а затем скачивать сводный список ингредиентов.

Проект состоит из React-клиента и Django REST API. Описание HTTP-интерфейса
находится в [OpenAPI-спецификации](docs/openapi-schema.yml).

## Возможности

- регистрация, вход по токену и изменение пароля;
- профили пользователей, аватары и подписки;
- рецепты с тегами, изображениями и ингредиентами;
- фильтрация рецептов по автору, тегам, избранному и корзине;
- избранное и список покупок;
- скачивание списка покупок в TXT;
- короткие ссылки на рецепты.

## Технологии

- Python 3
- Django
- Django REST Framework
- django-filter
- PostgreSQL
- Djoser
- React 17

## Локальный запуск API

Требуются Python 3.10+ и Node.js 18+.

```bash
git clone <URL-репозитория>
cd foodgram
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
export DEBUG=True
python manage.py migrate
python manage.py load_ingredients
python manage.py runserver
```

API будет доступен по адресу <http://127.0.0.1:8000/api/>.

Команда `load_ingredients` загружает данные из
[`data/ingredients.json`](data/ingredients.json). Она не защищена от
повторного запуска и добавит дубликаты ингредиентов, поэтому запускайте её
только для пустой базы.

### Переменные окружения backend

Настройки читаются из переменных окружения процесса (файл `.env` сам по себе
не загружается):

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `SECRET_KEY` | секретный ключ Django | случайный ключ на каждый запуск |
| `DEBUG` | режим отладки (`True` или `False`) | `False` |
| `ALLOWED_HOSTS` | допустимые хосты через запятую | `localhost,127.0.0.1` |

Для production обязательно задайте постоянный `SECRET_KEY`, `DEBUG=False` и
точный список `ALLOWED_HOSTS`.

## API и документация

- OpenAPI: [`docs/openapi-schema.yml`](docs/openapi-schema.yml)
- Redoc после запуска nginx: <http://localhost/api/docs/>
- Коллекция для Postman: [`postman_collection/foodgram.postman_collection.json`](postman_collection/foodgram.postman_collection.json)

Основные маршруты API:

| Маршрут | Назначение |
| --- | --- |
| `/api/auth/token/login/` | получить токен |
| `/api/users/` | пользователи и регистрация |
| `/api/users/subscriptions/` | подписки текущего пользователя |
| `/api/tags/` | теги |
| `/api/ingredients/` | ингредиенты и поиск |
| `/api/recipes/` | рецепты |

Полное описание всех эндпоинтов доступно в ReDoc.

## Структура проекта

```text
backend/              Django-проект и приложения api, recipes, users
frontend/             React-клиент
data/                 исходные данные ингредиентов
docs/                 OpenAPI-спецификация и Redoc
infra/                nginx и Docker Compose
postman_collection/   коллекция запросов Postman
```

## Автор

Проект выполнен в рамках курса **Яндекс Практикум**.

| Роль | GitHub |
|------|--------|
| Backend Developer | [Torb7](https://github.com/Torb7) |

## Адрес сервера: edagram.sytes.net
