FROM python:3.9

# fix CVE's by upgrading packages
RUN apt-get update && apt-get upgrade -y

#
# Setup non-Python environment and dependencies
#
# RUN apt-get install -y wkhtmltopdf

#
# Setup Python environment and dependencies
#
COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project false
RUN poetry install --only main --no-root

#
# Setup server
#
RUN mkdir /app
WORKDIR /app
COPY backend backend
RUN poetry install --only main

EXPOSE 80

RUN useradd -m myuser
#USER myuser

# converted to CMD [...]:
CMD ["gunicorn", "backend.backend_fargate:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "--workers", "2", "--max-requests", "500", "--log-level", "debug"]
