FROM python:3.12-slim

WORKDIR /code

EXPOSE 8080

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./ /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["bash", "-c", "alembic upgrade heads; uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4"]