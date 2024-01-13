# Веб-приложение "Фудграм".

Автор: [Vyacheslav Menyukhov](https://github.com/platsajacki) | menyukhov@bk.ru

https://menyukhov-foodgram.ddns.net/

Этот проект представляет собой веб-приложение "Фудграм", где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и использовать сервис "Список покупок" для создания списка продуктов, необходимых для приготовления блюд.

## Технологии

- Django, DRF
- PostgreSQL
- Docker, Docker Compose
- React

## Запуск проекта

Проект разделен на 4 контейнера: nginx, PostgreSQL, Django и React, запускаемые через docker-compose.

Для запуска проекта выполните следующие шаги:
1. Склонируйте репозиторий `foodgram-project-react` на свой компьютер:
   ```bash
    git clone https://github.com/platsajacki/foodgram-project-react.git
    ```

2. Создайте и заполните файл `.env` по образцу `.env.template`, разместите его в директории проекта.

3. Из директории проекта запустите проект в четырех контейнерах с помощью Docker Compose:
    ```bash
    docker compose up
    ```

4. Скопируйте фикстуры в проект:
    ```bash
    docker compose cp ./data/. backend:/app/foodgram/fixtures/
    ```

5. В контейнере с Django проведите миграцию, соберите статику и перенесите её в volume:
    ```bash
    docker compose exec backend python manage.py migrate
    docker compose exec backend python manage.py collectstatic
    docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

6. Если потребуется работа в панели администратора, создайте суперпользователя:
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```

7. Загрузите данные с ингредиентами и тегами:
    ```bash
    docker compose exec backend python manage.py loaddata /app/foodgram/fixtures/ingredients.json
    docker compose exec backend python manage.py loaddata /app/foodgram/fixtures/tags.json
    ```

8. Теперь вы можете обращаться к API по адресу: http://127.0.0.1/

## Прочее

Данные сохраняются в volumes для сохранения их состояния.
Для дальнейших инструкций по настройке проекта обратитесь к соответствующей документации.
