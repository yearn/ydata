FROM python:3.9-bullseye

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY . /app
RUN $HOME/.local/bin/poetry config virtualenvs.create false \
  && $HOME/.local/bin/poetry install --no-interaction --no-ansi

EXPOSE 8000
ENTRYPOINT ["bash", "entrypoint.sh"]