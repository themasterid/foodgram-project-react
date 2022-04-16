![foodgram-project-react Workflow Status](https://github.com/themasterid/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)
# Продуктовый помощник Foodgram

Проект доступен по адресу http://62.84.115.143/recipes

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере Yandex.Cloud в папку infra
```bash
ssh username@ip
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- Перенести файлы docker-compose.yml и default.conf на сервер.
- Заполнить в настройках репозитория секреты .env

```env
DB_ENGINE='django.db.backends.postgresql'
DB_NAME='foodgram'
POSTGRES_USER='foodgram_u'
POSTGRES_PASSWORD='xxx'
DB_HOST='127.0.0.1'
DB_PORT='5432'
SECRET_KEY='my_mega_secret_code_xxxxxxxxxxxxxxxxxxxxx'
ALLOWED_HOSTS='127.0.0.1, localhost'
```

Скопировать на сервер настройки docker-compose.yml, default.conf из папки infra.

```bash
scp docker-compose.yml username@server_ip:/home/<username>/
scp default.conf <username>@<server_ip>:/home/<username>/
```

## Запуск проекта через Docker

Собрать контейнер:
```bash
sudo docker-compose up -d
```
Выполнить следующие команды:
```bash
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate --noinput 
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Дополнительно можно наполнить DB ингредиентами и тэгами:
```bash
sudo docker-compose exec backend python manage.py load_tags
sudo docker-compose exec backend python manage.py load_ingrs
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

### Документация к API доступна после запуска
'''url
http://127.0.0.1/api/docs/
'''
