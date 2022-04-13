FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN echo 'we are running some # of cool things'
RUN ls
RUN pip3 install -r ./requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
