FROM python:3.7-slim
WORKDIR /app
RUN pip freeze > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
