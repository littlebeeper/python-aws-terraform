import argparse
import boto3

def main(key, recovery_days=7):
    client = boto3.client('secretsmanager')
    if recovery_days == 0:
        response = client.delete_secret(
            SecretId=key,
            ForceDeleteWithoutRecovery=True,
        )
    else:
        response = client.delete_secret(
            SecretId=key,
            RecoveryWindowInDays=recovery_days,
            ForceDeleteWithoutRecovery=False,
        )
    print(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete a secret in secrets manager')

    parser.add_argument('--key', '-k',
                        type=str,
                        required=True,
                        help='Key name')

    parser.add_argument('--recovery-days', '-rd',
                        type=int,
                        default=7,
                        help='Recovery window in days')

    args = parser.parse_args()
    main(args.key, args.recovery_days)
