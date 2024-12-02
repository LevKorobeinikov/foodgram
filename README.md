![workflow](https://github.com/LevKorobeinikov/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram

Foodgram — это сайт, где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на авторов. Зарегистрированные пользователи могут создавать «Список покупок» для удобства в приготовлении блюд.

Сайт доступен по [https://foooodgram.duckdns.org/](https://foooodgram.duckdns.org/).

## Стек проекта

- **Язык программирования**: Python
- **Фреймворк**: Django
- **База данных**: PostgreSQL
- **API**: Django Rest Framework
- **Система контроля версий**: Git
- **Инструменты разработки**: VSCode
- **Управление зависимостями**: pip, requirements.txt
- **Сервер**: Nginx
- **WSGI-сервер**: Gunicorn
- **Контейнеризация**: Docker
- **Аутентификационный бэкенд**: Djoser

## Как запустить проект

1. Клонировать репозиторий и перейти в него:
    ```bash
    git clone git@github.com:LevKorobeinikov/foodgram.git
    cd Foodgram
    ```

2. Создать и активировать виртуальное окружение:

    Для Windows:
    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```
    Для Linux/macOS:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Обновить PIP:
    Для Windows:
    ```bash
    python -m pip install --upgrade pip
    ```
    Для Linux/macOS:
    ```bash
    python3 -m pip install --upgrade pip
    ```

4. Установить зависимости из файла requirements.txt:
    ```bash
    pip install -r requirements.txt
    ```

5. Запустить проект с помощью Docker:
    На сервере создайте директорию `foodgram` и перейдите в неё:
    ```bash
    mkdir foodgram
    cd foodgram
    ```

6. Скопировать файл `docker-compose.production.yml` из текущего репозитория в корневую папку проекта `foodgram/`. В этой же папке создайте файл `.env` и заполните его согласно примеру:
    ```
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=db
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=*key*
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost,вашдомен
    ```

7. Выполнить git push:
    ```bash
    git push
    ```

8. Создать администратора сайта:
    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
    ```

## Ссылка на документацию

Находясь в папке `infra`, выполните команду:
    ```bash
    docker-compose up
    ```
При выполнении этой команды контейнер `frontend`, описанный в `docker-compose.yml`, подготовит файлы для фронтенд-приложения. После этого он прекратит свою работу.

Изучите фронтенд веб-приложения по адресу [http://localhost](http://localhost), а спецификацию API — по адресу [http://localhost/api/docs/](http://localhost/api/docs/).

## Автор проекта
 
[LevKorobeinikov](https://github.com/LevKorobeinikov)