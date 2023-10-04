import argparse

import boto3


def main(key, value):
    client = boto3.client('secretsmanager')
    response = client.create_secret(
        Name=key,
        SecretString=value
    )
    print(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a simple secret in secrets manager')

    parser.add_argument('--key', '-k',
                        type=str,
                        required=True,
                        help='Key name')

    parser.add_argument('--value', '-v',
                        type=str,
                        required=True,
                        help='Value')

    args = parser.parse_args()
    main(args.key, args.value)
