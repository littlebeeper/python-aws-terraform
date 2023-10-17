import argparse

import boto3


def main(key):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId=key
    )
    print(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a secret in secrets manager')

    parser.add_argument('--key', '-k',
                        type=str,
                        required=True,
                        help='Key name')

    args = parser.parse_args()
    main(args.key)
