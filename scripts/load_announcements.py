#!/usr/bin/env python3
"Load announcement messages into a DynamoDB table."
import argparse
import datetime
import sys
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def parse_args():
    "Parse command line arguments."
    parser = argparse.ArgumentParser(
        description="Load announcement messages into a DynamoDB table."
    )
    parser.add_argument(
        "--table",
        default="DEV_Announcement",
        help="DynamoDB table name. Defaults to DEV_Announcement.",
    )
    parser.add_argument(
        "--region",
        help="AWS region. If omitted, boto3 uses your normal AWS configuration.",
    )
    parser.add_argument(
        "--profile",
        help="AWS profile name. If omitted, boto3 uses your default profile.",
    )
    parser.add_argument(
        "--message",
        action="append",
        default=[],
        help="Announcement message to load. Can be passed more than once.",
    )
    parser.add_argument(
        "--file",
        help="Text file of announcement messages, one message per line.",
    )
    return parser.parse_args()


def build_session(profile):
    "Build a boto3 session."
    if profile:
        return boto3.Session(profile_name=profile)
    return boto3.Session()


def read_messages(args):
    "Return messages from --message and --file inputs."
    messages = list(args.message)

    if args.file:
        with open(args.file, encoding="utf-8") as file_obj:
            messages.extend(line.strip() for line in file_obj if line.strip())

    return messages


def key_value(attribute_type, value):
    "Return a DynamoDB-typed attribute value."
    if attribute_type == "N":
        return {"N": "1"}
    return {"S": value}


def build_item(message, key_schema, attribute_types):
    "Build a DynamoDB item containing the required key fields and Contents."
    now = datetime.datetime.now(datetime.UTC).isoformat()
    item = {"Contents": {"S": message}}

    for key in key_schema:
        name = key["AttributeName"]
        if name in item:
            continue

        value = str(uuid.uuid4())
        if key["KeyType"] == "RANGE":
            value = now

        item[name] = key_value(attribute_types.get(name, "S"), value)

    return item


def load_announcements(args):
    "Load announcement messages into DynamoDB."
    messages = read_messages(args)
    if not messages:
        print("No messages provided. Use --message or --file.", file=sys.stderr)
        return 1

    session = build_session(args.profile)
    dynamodb = session.client("dynamodb", region_name=args.region)
    table = dynamodb.describe_table(TableName=args.table)["Table"]
    key_schema = table["KeySchema"]
    attribute_types = {
        attr["AttributeName"]: attr["AttributeType"]
        for attr in table.get("AttributeDefinitions", [])
    }

    for message in messages:
        dynamodb.put_item(
            TableName=args.table,
            Item=build_item(message, key_schema, attribute_types),
        )
        print(f"Loaded announcement: {message}")

    return 0


def main():
    "Run the announcement loader."
    args = parse_args()

    try:
        return load_announcements(args)
    except (BotoCoreError, ClientError) as exc:
        print(f"Could not load announcements: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
