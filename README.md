# Дипломный проект "Фудграм". Я.Практикум

Автор: [Vyacheslav Menyukhov](https://github.com/platsajacki) | menyukhov@bk.ru

https://menyukhov-foodgram.ddns.net/

Этот проект представляет собой веб-приложение "Фудграм", где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и использовать сервис "Список покупок" для создания списка продуктов, необходимых для приготовления блюд.

## Технологии

- Фронтенд: React
- Бэкенд: Django
- База данных: PostgreSQL

## Запуск проекта

Проект разделен на три контейнера: nginx, PostgreSQL и Django, запускаемые через docker-compose. Файлы для сборки фронтенда хранятся в репозитории `foodgram-project-react` в папке `frontend`.

Для запуска проекта выполните следующие шаги:
1. Склонируйте репозиторий `foodgram-project-react` на свой компьютер.
2. Запустите проект в трёх контейнерах с помощью Docker Compose:
    ```
    docker compose up
    ```
3. Скопируйте фикстуры в проект:
    ```
    docker compose cp /data/. backend:/app/foodgram/fixtures/
    ```
4. Войдите в контейнер с Django проведите миграцию и соберите статику:
    ```
    docker compose exec -it backend bash
    python manage.py migrate
    python manage.py collectstatic
    ```
5. Загрузите данные с ингредиентами и тегами:
    ```
    python manage.py loaddata /app/foodgram/fixtures/ingredients.json
    python manage.py loaddata /app/foodgram/fixtures/tags.json
    ```
6. Если потребуется работа в панели администратора, создайте суперпользователя:
    ```
    python manage.py createsuperuser
    ```

## Прочее

Данные сохраняются в volumes для сохранения их состояния.
Для дальнейших инструкций по настройке проекта обратитесь к соответствующей документации.
