FROM python:latest

WORKDIR /code

COPY ./ /code/
RUN pip install --upgrade -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]