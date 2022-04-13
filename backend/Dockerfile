FROM python:3.7-slim
WORKDIR /app
COPY . .
COPY backend/requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY backend/ .
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
