# Switching Between SQLite and RDS IAM Authentication

This application chooses the database from environment variables.

## SQLite Mode

SQLite is used when `DB_HOST` is not set.

Use this mode for local development, low-cost demos, and portfolio hosting where persistent production data is not required.

Local terminal setup:

```bash
unset DB_HOST
unset DB_PORT
unset DB_NAME
unset DB_USER
unset DB_PASSWORD
unset DB_USE_IAM_AUTH
unset AWS_REGION
unset AWS_DEFAULT_REGION
unset LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN
```

Verify SQLite mode:

```bash
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE']); print(settings.DATABASES['default']['NAME'])"
```

Expected engine:

```text
django.db.backends.sqlite3
```

Apply the SQLite schema:

```bash
python manage.py migrate
```

## RDS IAM Mode

RDS is used when `DB_HOST` is set.

IAM authentication is used when `DB_USE_IAM_AUTH` is true. In this mode, the app generates temporary RDS auth tokens instead of using a static database password.

Local terminal setup:

```bash
export DB_HOST="appointment-scheduler-db.chkwukm2mwuq.us-east-2.rds.amazonaws.com"
export DB_PORT="3306"
export DB_NAME="appointments"
export DB_USER="appointment_web_user"
export AWS_REGION="us-east-2"
export AWS_DEFAULT_REGION="us-east-2"
export DB_USE_IAM_AUTH="true"
export LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN="1"
unset DB_PASSWORD
```

Verify RDS IAM mode:

```bash
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE']); print(settings.DATABASES['default']['HOST']); print(settings.DATABASES['default']['USER']); print(settings.DATABASES['default']['PASSWORD'] == '')"
```

Expected values:

```text
hairdresser_django.db.backends.mysql_iam
appointment-scheduler-db.chkwukm2mwuq.us-east-2.rds.amazonaws.com
appointment_web_user
True
```

## Elastic Beanstalk Environment Settings

For SQLite demo mode, do not set `DB_HOST`.

Example:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: hairdresser_django.settings
    DB_USE_IAM_AUTH: "false"
```

For RDS IAM mode, add the RDS variables:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: hairdresser_django.settings
    DB_HOST: appointment-scheduler-db.chkwukm2mwuq.us-east-2.rds.amazonaws.com
    DB_PORT: "3306"
    DB_NAME: appointments
    DB_USER: appointment_web_user
    AWS_REGION: us-east-2
    AWS_DEFAULT_REGION: us-east-2
    LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN: "1"
    DB_USE_IAM_AUTH: "true"
```

Do not store a database password for IAM mode. The app generates temporary IAM tokens at connection time.

## AWS Requirements For RDS IAM Mode

The runtime identity must be allowed to connect to the RDS database user.

Required IAM action:

```text
rds-db:connect
```

Required resource pattern:

```text
arn:aws:rds-db:us-east-2:471112960427:dbuser:db-EQRHZT236XDGTJIGFHULUVZKAI/appointment_web_user
```

The database security group must also allow inbound MySQL traffic on port `3306` from the runtime security group.

Examples:

```text
EKS: allow inbound 3306 from the EKS worker node security group.
Elastic Beanstalk: allow inbound 3306 from the Beanstalk EC2 instance security group.
```

## Key Rule

```text
No DB_HOST = SQLite
DB_HOST + DB_USE_IAM_AUTH=true = Amazon RDS with IAM authentication
```
