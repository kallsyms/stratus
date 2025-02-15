FROM python:3.11

ENV DEBIAN_FRONTEND=noninteractive \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    libeccodes-dev gdal-bin libgdal-dev

RUN pip install poetry

RUN mkdir /opt/wx_explore
WORKDIR /opt/wx_explore

COPY pyproject.toml poetry.lock /opt/wx_explore

RUN poetry install --no-root --no-interaction
RUN pip install gunicorn

COPY wx_explore /opt/wx_explore/wx_explore
RUN touch /opt/wx_explore/README.md
RUN pip install -e .

COPY data /opt/wx_explore/data

EXPOSE 8080

CMD ["gunicorn", "-b:8080", "--workers=1", "wx_explore.web.app:app"]
