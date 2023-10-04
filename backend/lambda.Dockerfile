FROM public.ecr.aws/lambda/python:3.9

# fix CVE's
RUN yum -y update pcre curl libcurl openssl openssl-libs glib2

# Copy only requirements to cache them in docker layer
WORKDIR ${LAMBDA_TASK_ROOT}
COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}/

# Project initialization:
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project false
RUN poetry install --only recalc --no-root

# Copy our package to the Docker image
COPY backend ${LAMBDA_TASK_ROOT}/backend

# copy over the env files
COPY .env.qa ${LAMBDA_TASK_ROOT}/.env.qa
COPY .env.production ${LAMBDA_TASK_ROOT}/.env.production

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "backend.backend_lambda.handler" ]
