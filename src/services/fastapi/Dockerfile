FROM python:3.9

WORKDIR /app

COPY . /app

RUN export PATH=$HOME/.local/bin:$PATH \
  && pip install poetry>=1.0.0

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

WORKDIR /app/src/services/fastapi

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
