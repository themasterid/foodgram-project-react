![foodgram-project-react Workflow Status](https://github.com/themasterid/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)
# Продуктовый помощник Foodgram (дополнить реадми)

Проект доступен по адресу ... изменено.

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере ВМ Yandex.Cloud:

```bash
ssh username@ip
```
```bash
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```
```bash
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```bash
sudo chmod +x /usr/local/bin/docker-compose
```

Создайте папку infra:

```bash
mkdir infra
```

- Перенести файлы docker-compose.yml и default.conf на сервер.

```bash
scp docker-compose.yml username@server_ip:/home/<username>/
```

```bash
scp default.conf <username>@<server_ip>:/home/<username>/
```

- Создайте файл .env в дериктории infra:


```bash
touch .env
```

- Заполнить в настройках репозитория секреты .env

```python
DB_ENGINE = 'django.db.backends.postgresql'
POSTGRES_DB = 'foodgram'
POSTGRES_USER = 'foodgram_u'
POSTGRES_PASSWORD = 'foodgram_u_pass'
DB_HOST = 'db'
DB_PORT = '5432'
SECRET_KEY = 'secret'
ALLOWED_HOSTS = '127.0.0.1, backend'
DEBUG = False
```

Скопировать на сервер настройки docker-compose.yml, default.conf из папки infra.

## Запуск проекта через Docker
- В папке infra выполнить команду, что бы собрать контейнер:
```bash
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```bash
sudo docker-compose exec backend python manage.py makemigrations
```
```bash
sudo docker-compose exec backend python manage.py migrate --noinput
```
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```
```bash
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить DB ингредиентами и тэгами:

```bash
sudo docker-compose exec backend python manage.py load_tags
```
```bash
sudo docker-compose exec backend python manage.py load_ingrs
```

## Запуск проекта в dev-режиме

- Установить и активировать виртуальное окружение:

```bash
cd foodgram-project-react
```

```bash
python3 -m venv env
```

```bash
source /venv/bin/activated
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r backend/requirements.txt
```

- Создайте базу и пользователя в Postgresql:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE basename;
```

```sql
CREATE USER username WITH ENCRYPTED PASSWORD 'password';
```

```sql
GRANT ALL PRIVILEGES ON DATABASE basename TO username;
```

- В папке с проектом создаем файл .env:
```bash
touch backend/foodgram/.env
```

С следующим содержанием db_name и db_user указываем свои:
```python
DB_ENGINE = 'django.db.backends.postgresql'
POSTGRES_DB = 'foodgram'
POSTGRES_USER = 'foodgram_u'
POSTGRES_PASSWORD = 'foodgram_u_pass'
DB_HOST = 'localhost'
DB_PORT = '5432'
SECRET_KEY = 'secret'
ALLOWED_HOSTS = '127.0.0.1, backend, localhost'
DEBUG = False
```

- Выполняем и применяем миграции, создаем суперпользователя и собираем статику:

```bash
python backend/manage.py makemigrations
```

```bash
python backend/manage.py migrate
```

```bash
python backend/manage.py createsuperuser
```

```bash
python backend/manage.py collectstatic --no-input
```

(Дописать 16.01.2023)
- Запускаем сервер командой:

```bash
python backend/manage.py runserver
```

### Документация к API доступна после запуска

```url
http://127.0.0.1/api/docs/
```

Автор: [Клепиков Дмитрий](https://github.com/themasterid)
