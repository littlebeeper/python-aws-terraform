import argparse

import subprocess

from dotenv import find_dotenv, dotenv_values
import boto3
from botocore.errorfactory import ClientError
from enum import Enum

from backend.env import Environment

TEST_CONTAINER_NAME = 'lambda-local'
BUILD_NAME = 'lambda'
FE_S3_BUCKET = 'mogara-fe-assets'

ENV_S3_BUCKET = 'mogara-api-env-{0}'


class DeployAction(Enum):
    BUILD_API_IMAGE = 1
    LOCAL_INSPECTION = 2
    PUSH_IMAGE_TO_ECR = 3
    UPDATE_CONFIG = 4
    DEPLOY_API = 5


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


def run_command(command, dryrun, cwd=None):
    if dryrun:
        print('DRYRUN', end=' ')
    print(command)
    if not dryrun:
        print(subprocess.check_output(command, shell=True, cwd=cwd).decode("utf-8"))


def run_non_blocking_command(command, dryrun):
    if dryrun:
        print('DRYRUN', end=' ')
    print(command)
    if not dryrun:
        process = subprocess.Popen(command, shell=True, text=True)
        # out, err = process.communicate()
        # return out, err


def build_container(progress, dryrun, clear_cache):
    if clear_cache:
        run_command('docker system prune -a -f', dryrun=dryrun)
    run_command(
        'docker build --platform linux/amd64 -t {0}:latest --progress={1} -f recalc.Dockerfile .'.format(BUILD_NAME, progress),
        dryrun=dryrun)


def push_image_to_registry(env, dryrun, name='recalc') -> None:
    env_values = get_env_values(env)
    ecr_repo = env_values['ECR_REPO']

    ecr_path = f"{ecr_repo}/{name}-{env}:latest"
    run_command(f"docker tag {BUILD_NAME}:latest {ecr_path}",
                dryrun=dryrun)
    run_command('aws ecr get-login-password | docker login --username AWS --password-stdin {0}'.format(ecr_repo),
                dryrun=dryrun)
    run_command('docker push {0}'.format(ecr_path),
                dryrun=dryrun)


def update_config(env, dryrun, name='recalc') -> None:
    env_values = get_env_values(env)
    # create a list of env variables to pass to the lambda
    env_vars = ""
    for key, value in env_values.items():
        env_vars += f"{key}={value}, "

    # escape &
    env_vars = env_vars.replace('&', '\&')

    # add curly braces
    env_vars = "{" + env_vars[:-2] + "}"

    # update-function-configuration
    run_command(
        f"aws lambda update-function-configuration --function-name {name}-{env} --environment \"Variables={env_vars}\"",
        dryrun=dryrun)

    # wait until the function is updated
    run_command(f"aws lambda wait function-updated --function-name {name}-{env}", dryrun=dryrun)


def deploy(env, dryrun, name='recalc') -> None:
    env_values = get_env_values(env)
    ecr_repo = env_values['ECR_REPO']

    ecr_path = f"{ecr_repo}/{name}-{env}:latest"

    # update-function-code
    run_command(f"aws lambda update-function-code --function-name {name}-{env} --image-uri {ecr_path}", dryrun=dryrun)

    # wait until the function is updated
    run_command(f"aws lambda wait function-updated --function-name {name}-{env}", dryrun=dryrun)


def local_inspection(env: Environment, dryrun):
    # TODO: make this auto locally inspectable via AWS SAM
    app_name = env.app_name()
    print("Note: Ensure you've configured the appropriate AWS creds via 'aws configure configure --profile {0}'".format(
        app_name))

    # TODO: convert aws_profile_name to be person agnostic
    # TODO: switch back to DEVELOPMENT
    development_env_values = get_env_values(Environment.QA, aws_profile_name="jay")

    run_command('docker rm -f {0} || true'.format(TEST_CONTAINER_NAME), dryrun=dryrun)
    run_command('export PORT=5001', dryrun=dryrun)

    # compile list of docker env variables
    config = ' '.join(map(lambda x: '-e {0}={1}'.format(x[0], x[1]), development_env_values.items()))

    # make sure characters are properly escaped (e.g. &)
    config = config.replace('&', '\&')

    run_command(
        # TODO add back -d
        f"docker run --rm -e PORT=5001 {config} -p 5001:5001 --name {TEST_CONTAINER_NAME} --platform linux/amd64 {BUILD_NAME}:latest",
        dryrun=dryrun)
    # amount of time
    # if not dryrun:
    #     time.sleep(10)
    # run_command(
    #     "curl http://0.0.0.0:5001/ping -vvv",
    #     dryrun=dryrun)
    # answer = input("Did this test request succeed? (y/n): ")
    # if answer.lower() != 'y':
    #     raise "Local testing failed"
    # else:
    #     print("Local testing succeeded")
    #     run_command('docker rm -f {0} || true'.format(TEST_CONTAINER_NAME), dryrun=dryrun)



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
        build_container(
            progress=build_progress,
            clear_cache=clear_build_cache,
            dryrun=dryrun)

    if DeployAction.LOCAL_INSPECTION in actions:
        print('LOCAL_INSPECTION')
        local_inspection(
            env=env,
            dryrun=dryrun)

    if DeployAction.PUSH_IMAGE_TO_ECR in actions:
        print('PUSH_IMAGE_TO_REGISTRY')
        push_image_to_registry(
            env=env,
            dryrun=dryrun)

    if DeployAction.UPDATE_CONFIG in actions:
        print('UPDATE_CONFIG')
        update_config(
            env=env,
            dryrun=dryrun)

    if DeployAction.DEPLOY_API in actions:
        print('DEPLOY_API')
        deploy(env=env, dryrun=dryrun)


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
                        choices=[Environment.QA.name.lower(), Environment.PRODUCTION.name.lower()],
                        help='Environment to deploy to')

    parser.add_argument('--real', '-r',
                        required=False,
                        default=False,
                        action='store_true',
                        help="Whether we're deploying for real or this is a dryrun")

    parser.add_argument('--actions', '-a',
                        required=False,
                        # all stages except for local_inspection
                        default=[x.name.lower() for x in DeployAction if x != DeployAction.LOCAL_INSPECTION],
                        nargs='+',
                        type=str,
                        help=f"Stages to run e.g. {' '.join([x.name.lower() for x in DeployAction])}")

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

    args = parser.parse_args()

    actions: list[DeployAction] = [DeployAction[x.upper()] for x in args.actions]

    main(
        env=Environment[args.env.upper()],
        build_progress=args.build_progress,
        actions=list(set(actions)),
        clear_build_cache=args.clear_build_cache,
        dryrun=not args.real)
