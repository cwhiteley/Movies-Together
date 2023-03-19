FROM python:3.10

WORKDIR opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG PORT


COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt



CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8011"]

