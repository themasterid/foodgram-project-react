FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip freeze > requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
