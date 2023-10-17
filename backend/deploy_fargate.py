import argparse
import os
import subprocess
import time

import magic
from dotenv import find_dotenv, dotenv_values
import boto3
from botocore.errorfactory import ClientError
from enum import Enum

from backend.env import Environment

SERVICE_NAME = 'jaygokhale'

TEST_CONTAINER_NAME = f"{SERVICE_NAME}-api-container"
IMAGE_NAME = f"{SERVICE_NAME}-api"


def ecr_repo_prefix():
    return f"{ACCOUNT_ID}.dkr.ecr.us-west-1.amazonaws.com"


def service_name(env):
    return f"{SERVICE_NAME}-api-{env}"


def ecr_repo(env):
    return f"{ACCOUNT_ID}.dkr.ecr.us-west-1.amazonaws.com/{service_name(env)}"


def fe_s3_bucket(env):
    return f"{SERVICE_NAME}-fe-assets-{env}"


def env_s3_bucket(env):
    return f"{SERVICE_NAME}-env-{env}"


# TODO generify
BUILD_DIR = "backend/"
ACCOUNT_ID = "940730671260"


class DeployAction(Enum):
    BUILD_API_IMAGE = 1
    LOCAL_INSPECTION = 2
    PUSH_ENV_FILE_TO_S3 = 3
    PUSH_IMAGE_TO_ECR = 4
    DEPLOY_API = 5

    BUILD_FE = 6
    DEPLOY_FE = 7


BACKEND_ACTIONS = [
    DeployAction.BUILD_API_IMAGE,
    DeployAction.LOCAL_INSPECTION,
    DeployAction.PUSH_ENV_FILE_TO_S3,
    DeployAction.PUSH_IMAGE_TO_ECR,
    DeployAction.DEPLOY_API,
]

FRONTEND_ACTIONS = [
    DeployAction.BUILD_FE,
    DeployAction.DEPLOY_FE,
]

FILE_EXT_TO_MIME_TYPE = {
    '.js': 'text/javascript',
    '.css': 'text/css',
}


def get_mime_type(file_name):
    ext = os.path.splitext(file_name)[1]
    if ext in FILE_EXT_TO_MIME_TYPE:
        return FILE_EXT_TO_MIME_TYPE[ext]
    return magic.from_file(file_name, mime=True)


def fe_file_needs_update(bucket, key, content_type):
    s3 = boto3.client('s3')
    try:
        obj = s3.head_object(Bucket=bucket, Key=key)

        if content_type != obj['ResponseMetadata']['HTTPHeaders']['content-type']:
            return True

        return False
    except ClientError:
        # Not found
        pass
    finally:
        return True


def s3_exists(bucket, key, ):
    s3 = boto3.client('s3')
    try:
        print(bucket, key)
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        # Not found
        pass
    return False


def run_command(command, dryrun, cwd=None, default_response=""):
    if dryrun:
        print('DRYRUN', end=' ')
    print(command)
    if not dryrun:
        response = subprocess.check_output(command, shell=True, cwd=cwd).decode("utf-8").strip()
        print(response)
        return response
    else:
        return default_response


def run_non_blocking_command(command, dryrun):
    if dryrun:
        print('DRYRUN', end=' ')
    print(command)
    if not dryrun:
        process = subprocess.Popen(command, shell=True, text=True)
        # out, err = process.communicate()
        # return out, err


def build_fe_assets(env: Environment, dryrun):
    # needed to run/test locally
    run_command('yarn build:development',
                cwd='backend/srv-fe',
                dryrun=dryrun)
    if env != Environment.DEVELOPMENT:
        run_command('yarn build:{0}'.format(env),
                    cwd='backend/srv-fe',
                    dryrun=dryrun)


def deploy_fe_assets(env: Environment, dryrun):
    env_values = get_env_values(env)
    build_path = env_values['REACT_BUILD_PATH']
    s3 = boto3.client('s3')
    print("build_path", build_path)
    for root, dirs, files in os.walk(build_path):
        for file in files:
            full_file_path = os.path.join(root, file)
            key = full_file_path[len(build_path) + 1:]
            assert os.path.exists(full_file_path)
            mime_type = get_mime_type(full_file_path)
            extra_args = {'ContentType': mime_type}
            if file == 'index.html':
                extra_args['CacheControl'] = 'no-cache, no-store'

            bucket = fe_s3_bucket(env)

            if file != 'index.html' and not fe_file_needs_update(bucket, key, mime_type):
                print(f"Skipping {file} already exists")
                continue

            print("Uploading {0} to {1}".format(full_file_path, f"{bucket}/{key}"))
            print("With args: ", extra_args)
            if not dryrun:
                s3.upload_file(full_file_path, bucket, key, ExtraArgs=extra_args)


def build_api_server(progress, dryrun, clear_cache):
    if clear_cache:
        run_command('docker system prune -a -f', dryrun=dryrun)
    run_command(
        'docker build --platform linux/amd64 -t {0}:latest --progress={1} -f fargate.Dockerfile .'.format(IMAGE_NAME,
                                                                                                          progress),
        dryrun=dryrun)


def push_env_file_to_s3(env, dryrun) -> None:
    # push up new environment variables to s3
    if not dryrun:
        s3 = boto3.client('s3')
        s3.upload_file(resolve_env_file(env), env_s3_bucket(env), '.env')


def push_image_to_registry(env, dryrun) -> None:
    run_command(
        f"aws ecr get-login-password | docker login --username AWS --password-stdin {ecr_repo_prefix()}",
        dryrun=dryrun)
    # get docker image id

    repo = ecr_repo(env)

    # push the :latest tag
    image_tag = run_command(
        f"docker images --filter=reference={IMAGE_NAME} --format '{{{{.ID}}}}'",
        dryrun=dryrun, default_response="default")
    for ecr_path in [f"{repo}:latest", f"{repo}:{image_tag}"]:
        run_command(f"docker tag {IMAGE_NAME}:latest {ecr_path}",
                    dryrun=dryrun)
        run_command('docker push {0}'.format(ecr_path),
                    dryrun=dryrun)


def deploy(env, dryrun) -> None:
    # kick off deployment
    run_command(f'aws ecs update-service --cluster {service_name(env)} --service {service_name(env)} --force-new-deployment',
                dryrun=dryrun)

    # wait for deployment to finish
    run_command(f'aws ecs wait services-stable --cluster {service_name(env)} --service {service_name(env)}',
                dryrun=dryrun)


def local_inspection(env: Environment, dryrun):
    # TODO: convert aws_profile_name to be person agnostic
    development_env_values = get_env_values(Environment.DEVELOPMENT, aws_profile_name="jay")

    run_command('docker rm -f {0} || true'.format(TEST_CONTAINER_NAME), dryrun=dryrun)
    # run_command('export PORT=80', dryrun=dryrun)
    config = ' '.join(map(lambda x: '-e {0}={1}'.format(x[0], x[1]), development_env_values.items()))

    run_command(
        f"docker run -d --rm "
        f"-e SRV_ENV={Environment.DEVELOPMENT} "
        f"-e PORT=80 {config} "
        f"-p 5001:80 "
        f"--name {TEST_CONTAINER_NAME} "
        f"--platform linux/amd64 {IMAGE_NAME}:latest",
        dryrun=dryrun)
    # amount of time
    if not dryrun:
        time.sleep(10)
    print("Ready for testing")
    run_command(
        "curl http://0.0.0.0:5001/ping -vvv",
        dryrun=dryrun)
    answer = input("Did this test request succeed? (y/n): ")
    if answer.lower() != 'y':
        raise "Local testing failed"
    else:
        print("Local testing succeeded")
        run_command('docker rm -f {0} || true'.format(TEST_CONTAINER_NAME), dryrun=dryrun)


def resolve_env_file(env):
    env_file = '.env.{0}'.format(env)
    return find_dotenv(filename=env_file, raise_error_if_not_found=True)


def get_env_values(env: Environment, aws_profile_name=None):
    env_values = dotenv_values(dotenv_path=resolve_env_file(env))

    if aws_profile_name:
        session = boto3.Session(profile_name=aws_profile_name)
        credentials = session.get_credentials()
        env_values['AWS_ACCESS_KEY_ID'] = credentials.access_key
        env_values['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
        env_values['AWS_REGION'] = session.region_name

    return env_values


def main(env: Environment, actions, build_progress, clear_build_cache, dryrun):
    if dryrun:
        print("Note: Running in DRYRUN mode. Proposed actions will be printed but no action will be taken")

    if DeployAction.BUILD_API_IMAGE in actions:
        print('BUILD_API_IMAGE')
        build_api_server(
            progress=build_progress,
            clear_cache=clear_build_cache,
            dryrun=dryrun)

    if DeployAction.LOCAL_INSPECTION in actions:
        print('LOCAL_INSPECTION')
        local_inspection(
            env=env,
            dryrun=dryrun)

    if DeployAction.PUSH_ENV_FILE_TO_S3 in actions:
        print('PUSH_ENV_FILE_TO_S3')
        push_env_file_to_s3(
            env=env,
            dryrun=dryrun)

    if DeployAction.PUSH_IMAGE_TO_ECR in actions:
        print('PUSH_IMAGE_TO_REGISTRY')
        push_image_to_registry(
            env=env,
            dryrun=dryrun)

    if DeployAction.DEPLOY_API in actions:
        print('DEPLOY_API')
        deploy(env=env, dryrun=dryrun)

    if DeployAction.BUILD_FE in actions:
        print('BUILD_FE')
        build_fe_assets(
            env=env,
            dryrun=dryrun)

    if DeployAction.DEPLOY_FE in actions:
        print('DEPLOY_FE')
        deploy_fe_assets(env=env, dryrun=dryrun)


if __name__ == '__main__':
    class ExplicitDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
        def _get_help_string(self, action):
            if action.default in (None, False):
                return action.help
            return super()._get_help_string(action)


    parser = argparse.ArgumentParser(
        description='Deployment script',
        formatter_class=ExplicitDefaultsHelpFormatter
    )

    parser.add_argument('--env', '-e',
                        dest='env',
                        type=str,
                        required=True,
                        choices=[Environment.STAGING.name.lower(), Environment.PRODUCTION.name.lower()],
                        help='Environment to deploy to')

    parser.add_argument('--real', '-r',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether we're deploying for real or this is a dryrun")

    parser.add_argument('--backend', '-b',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether we're deploying the backend or not")

    parser.add_argument('--frontend', '-f',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether we're deploying the frontend or not")

    parser.add_argument('--actions', '-a',
                        required=False,
                        default=[],
                        nargs='+',
                        type=str,
                        help=f"Stages to run e.g. {', '.join([x.name.lower() for x in DeployAction])}")

    parser.add_argument('--clear-build-cache', '-cc',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether to clear the docker cache before building the image")

    parser.add_argument('--build-progress', '-bp',
                        type=str,
                        required=False,
                        default='auto',
                        choices=['plain', 'auto', 'tty'],
                        help='How to display progress during the build')

    parser.add_argument('--skip-local-inspection', '--sli',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether to skip the local inspection step")

    args = parser.parse_args()

    actions: set[DeployAction] = set([DeployAction[x.upper()] for x in args.actions])
    if args.backend:
        actions.update(BACKEND_ACTIONS)

    if args.frontend:
        actions.update(FRONTEND_ACTIONS)

    if args.skip_local_inspection and DeployAction.LOCAL_INSPECTION in actions:
        actions.discard(DeployAction.LOCAL_INSPECTION)

    if len(actions) == 0:
        raise ValueError("No actions specified")

    main(
        env=Environment[args.env.upper()],
        build_progress=args.build_progress,
        actions=list(actions),
        clear_build_cache=args.clear_build_cache,
        dryrun=not args.real)
