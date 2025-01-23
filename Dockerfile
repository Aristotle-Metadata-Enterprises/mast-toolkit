FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE web.settings

# Install python package management tools
RUN pip install --upgrade setuptools pip poetry

COPY ./app /usr/src/app/
COPY ./poetry.lock /usr/src/
COPY ./pyproject.toml /usr/src/
WORKDIR /usr/src

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

ENV PYTHONPATH=/usr/src/app

# Expose the port that the Django app will run on
EXPOSE 8000

# Run the command to start the Gunicorn server
CMD ["gunicorn", "web.wsgi:application", "-b", "0.0.0.0:8000"]
