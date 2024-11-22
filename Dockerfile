FROM python:3.12-slim-bookworm AS python

COPY . /app

WORKDIR /app

RUN pip install -r requirement.txt

EXPOSE 8000

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]