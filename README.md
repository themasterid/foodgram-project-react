# Продуктовый помошник Foodgram

[![foodgram-project-react workflow](https://github.com/themasterid/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=status)](https://github.com/themasterid/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

# Проект доступен по адресу 

http://themasterid.sytes.net/

Супер пользователь:
```
email: fake@fake.fake
password: fakegrampassword
```
## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере Yandex.Cloud
```bash
ssh <username>@<server_ip>
sudo apt install docker.io
https://docs.docker.com/compose/install/ # docker-compose
```
- Заполнить в настройках репозитория секреты .env

```env
DB_ENGINE='django.db.backends.postgresql'
DB_NAME='foodgram'
POSTGRES_USER='foodgram'
POSTGRES_PASSWORD='xxx'
DB_HOST='127.0.0.1'
DB_PORT='5432'
SECRET_KEY='my_mega_secret_code_xxxxxxxxxxxxxxxxxxxxx'
ALLOWED_HOSTS='127.0.0.1, localhost'
```
- В docker-compose web:image установить свой контейнер

Скопировать на сервер настройки infra, fronted, docs.
```bash
scp -r docs/ <username>@<server_ip>:/home/<username>/docs/
scp -r infra/ <username>@<server_ip>:/home/<username>/infra/
scp -r frontend/ <username>@<server_ip>:/home/<username>/frontend/
```

## Запуск проекта через Docker

Собрать контейнер:
```bash
sudo docker-compose up -d
```
Выполнить следующие команды:
```bash
sudo docker-compose exec web python manage.py makemigrations
sudo docker-compose exec web python manage.py migrate --noinput 
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Дополнительно можно наполнить DB ингредиентами и тэгами:
```bash
sudo docker-compose exec web python manage.py load_tags
sudo docker-compose exec web python manage.py load_ingrs
```


## Запуск проекта в dev-режиме

- Установить и активировать виртуальное окружение
- Установить зависимости из файла requirements.txt
```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```
- Выполнить миграции:
```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

- Для загрузки ингредиентов и тэгов:
```bash
sudo docker-compose exec web python manage.py load_tags
sudo docker-compose exec web python manage.py load_ingredients
```

### Документация к API доступна после запуска
http://127.0.0.1/api/docs/
...
