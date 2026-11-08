# Foodgram

Foodgram — сервис публикации рецептов. Пользователь может создавать и редактировать собственные рецепты, подписываться на авторов, добавлять рецепты в избранное и список покупок, а также скачивать список ингредиентов.

Проект состоит из React-клиента и Django REST API. В production-сценарии приложение запускается в Docker Compose в четырёх контейнерах: PostgreSQL, backend, frontend и nginx-шлюз.

## Возможности

- регистрация и токенная авторизация по адресу электронной почты;
- просмотр пользователей, рецептов, тегов и ингредиентов;
- создание, редактирование и удаление рецептов;
- поиск ингредиентов по началу названия;
- фильтрация рецептов по автору, тегам, избранному и списку покупок;
- добавление и удаление рецептов из избранного и списка покупок;
- генерация и скачивание списка покупок в текстовом формате;
- подписки на авторов и просмотр ленты подписок;
- загрузка аватара пользователя;
- получение короткой ссылки на рецепт;
- административная зона Django.

## Стек

Backend:

- Python 3.12;
- Django 5.2;
- Django REST Framework;
- Djoser и Token Authentication;
- django-filter;
- PostgreSQL 14;
- Gunicorn.
- Pytest

Frontend:

- React 17;
- React Router 5;
- Create React App.

Инфраструктура: Docker, Docker Compose, nginx, GitHub Actions и Docker Hub.

## Структура проекта

```text
.
├── backend/                    # Django-проект и REST API
│   ├── api/                    # viewset'ы, сериализаторы, фильтры и права
│   ├── recipes/                # рецепты, теги, ингредиенты и связи
│   ├── users/                  # пользователи, подписки и пользовательские списки
│   ├── tests/                  # backend-тесты
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React-приложение
├── nginx/                      # конфигурация и Dockerfile nginx
├── data/                       # исходные ингредиенты и fixture
├── docs/                       # OpenAPI-схема и Redoc
├── docker-compose.yml          # сборка и запуск локально
├── docker-compose.production.yml
└── .github/workflows/main.yml  # CI/CD
```

## Модели данных

Основные модели проекта:

- `Recipe` — название, описание, изображение, время приготовления, автор, теги и ингредиенты;
- `Tag` — название и уникальный slug;
- `Ingredient` — название и единица измерения.

Для хранения количества ингредиента используется промежуточная модель `RecipeIngredients`.

Дополнительные модели:

- `User` — пользователь с уникальными email и username, именем, фамилией и аватаром;
- `Follow` — подписка одного пользователя на другого;
- `Favorites` — связь пользователя с избранным рецептом;
- `ShoppingCart` — связь пользователя с рецептом в списке покупок.

## Админ-зона

Административная зона доступна по адресу `/admin/`.

В ней настроены:

- поиск пользователей по username и email;
- список рецептов с названием, автором и датой публикации;
- поиск рецептов по названию и автору;
- фильтрация рецептов по тегам;
- отображение количества добавлений рецепта в избранное;
- inline-редактирование ингредиентов рецепта с количеством;
- список ингредиентов с единицей измерения и поиском по названию;
- отображение количества рецептов для тегов и ингредиентов.

## API

Все API-маршруты имеют префикс `/api/`. Подробная OpenAPI-схема находится в [docs/openapi-schema.yml](docs/openapi-schema.yml), HTML-версия документации — в [docs/redoc.html](docs/redoc.html).

Основные маршруты:

| Раздел | Маршруты | Доступ |
| --- | --- | --- |
| Авторизация | `POST /api/auth/token/login/`, `POST /api/auth/token/logout/` | регистрация пользователя — без авторизации; операции с токеном — по назначению |
| Пользователи | `/api/users/`, `/api/users/{id}/`, `/api/users/me/` | просмотр — публичный, изменения — для авторизованных |
| Подписки | `/api/users/subscriptions/`, `/api/users/{id}/subscribe/` | авторизованные |
| Теги | `GET /api/tags/`, `GET /api/tags/{id}/` | публичный доступ |
| Ингредиенты | `GET /api/ingredients/`, `GET /api/ingredients/{id}/` | публичный доступ |
| Рецепты | `/api/recipes/`, `/api/recipes/{id}/` | просмотр — публичный, запись — для авторизованных |
| Избранное | `/api/recipes/{id}/favorite/` | авторизованные |
| Список покупок | `/api/recipes/{id}/shopping_cart/`, `GET /api/recipes/download_shopping_cart/` | авторизованные |
| Короткая ссылка | `GET /api/recipes/{id}/get-link/` | публичный доступ |

Для защищённых запросов используется заголовок:

```http
Authorization: Token <токен>
```

Список рецептов поддерживает параметры `author`, `tags`, `is_favorited`, `is_in_shopping_cart`, `page` и `limit`. Один тег передаётся одним параметром `tags`; при выборе нескольких тегов параметр повторяется.

## Локальный запуск API

```bash
git clone https://github.com/Torb7/foodgram
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

## Быстрый запуск в Docker

Необходимы Docker и Docker Compose Plugin.

1. Создайте в корне проекта файл `.env`:

   ```dotenv
   POSTGRES_USER=<django_user>
   POSTGRES_PASSWORD=<password>
   POSTGRES_DB=<db>
   DB_HOST=<host>
   DB_PORT=<port>
   SECRET_KEY=<key>
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost:8080
   ```

2. Соберите образы и запустите сервисы:

   ```bash
   docker compose up -d --build
   ```

3. Выполните миграции, соберите статику и загрузите справочник ингредиентов:

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --noinput
   docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
   docker compose exec backend python manage.py load_ingredients
   ```

4. Создайте администратора:

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

После запуска:

- веб-приложение: <http://localhost:8080>;
- админ-зона: <http://localhost:8080/admin/>;
- API: <http://localhost:8080/api/>.

В локальном compose nginx-сервис называется `gateway`, но внутри используется образ nginx. Frontend-контейнер только собирает React-приложение и копирует результат в общий volume `static`; запросы к приложению обслуживает nginx.

## Хранение данных

Compose использует следующие named volumes:

- `pg_data` — данные PostgreSQL;
- `static` — собранная Django- и React-статика;
- `media` — загруженные изображения рецептов и аватары.

Удаление контейнеров через `docker compose down` не удаляет эти volumes. Для полного удаления данных потребуется отдельная команда `docker compose down -v`.

## Production и CI/CD

Файл `docker-compose.production.yml` запускает готовые образы backend, frontend и gateway из Docker Hub, а PostgreSQL использует официальный образ `postgres:14`. Публичный порт gateway — `8080`; фактический адрес сервиса имеет вид `http://<IP_сервера>:8080` или зависит от настроенного домена.

Workflow [.github/workflows/main.yml](.github/workflows/main.yml) запускается при push в ветку `main` и выполняет следующие этапы:

1. поднимает PostgreSQL 14 как service container;
2. устанавливает Python 3.12, запускает flake8 и pytest;
3. собирает и публикует образы backend, frontend и gateway в Docker Hub;
4. копирует production compose на сервер по SSH;
5. выполняет `docker compose pull`, перезапускает сервисы, применяет миграции и собирает статику.

Для GitHub Actions необходимы secrets:

| Secret | Назначение |
| --- | --- |
| `DOCKER_USERNAME` | логин Docker Hub |
| `DOCKER_PASSWORD` | пароль или access token Docker Hub |
| `HOST` | IP-адрес или доменное имя сервера |
| `USER` | SSH-пользователь |
| `SSH_KEY` | приватный SSH-ключ |

Перед первым production-деплоем проверьте, что имена образов в `docker-compose.production.yml` совпадают с Docker Hub username, используемым workflow, и что на сервере создан `.env` с production-значениями. Секреты и данные PostgreSQL должны храниться вне репозитория.

