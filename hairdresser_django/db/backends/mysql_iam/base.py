import os

import boto3
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper


class DatabaseWrapper(MySQLDatabaseWrapper):
    "MySQL backend that uses a fresh RDS IAM auth token for each new connection."

    def get_connection_params(self):
        params = super().get_connection_params()
        params["password"] = boto3.client("rds").generate_db_auth_token(
            DBHostname=self.settings_dict["HOST"],
            Port=int(self.settings_dict.get("PORT") or 3306),
            DBUsername=self.settings_dict["USER"],
            Region=os.environ.get("AWS_REGION", "us-east-2"),
        )
        return params
