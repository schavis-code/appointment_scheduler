# Appointment Scheduler Project -- Developer Handoff

## Project Overview

This is a Django-based appointment scheduler that was originally
provided as part of an AWS lab. The goal is to modernize it into a
production-quality portfolio project using AWS best practices.

The project currently runs locally on macOS (VS Code) and will
eventually deploy through AWS CI/CD.

## Development Environment

-   macOS
-   VS Code
-   Python virtual environment (.venv)

### Source Control

-   Git
-   GitHub (primary repository)

### AWS

Region: `us-east-2`

Services configured: - GitHub - CodeBuild - CodePipeline - IAM - Amazon
RDS MySQL

## Database

### Engine

-   Amazon RDS MySQL 8.4.x
-   Instance: `db.t4g.micro`

Development configuration: - Public endpoint - Security group restricted
to developer's IP - Encryption enabled - Automated backups enabled

## Authentication

Enabled: - IAM Database Authentication - SSL/TLS required

Database users:

### Master

`masteradmin`

### Application Admin

`appointment_admin` - AWSAuthenticationPlugin - Full privileges

### Web Application

`appointment_web_user` - AWSAuthenticationPlugin - SELECT - INSERT -
UPDATE - DELETE

## Database Name

`appointments`

## Current Database Schema

### customers

-   id
-   first_name
-   last_name
-   email
-   phone
-   created_at

### hairdressers

-   id
-   first_name
-   last_name
-   email
-   active
-   created_at

### services

-   id
-   name
-   description
-   duration_minutes
-   price
-   active
-   created_at

### appointments

-   id
-   customer_id
-   hairdresser_id
-   service_id
-   appointment_start
-   appointment_end
-   status (VARCHAR(20), default `scheduled`)
-   notes
-   created_at
-   updated_at

Foreign Keys: - customer_id → customers.id - hairdresser_id →
hairdressers.id - service_id → services.id

Indexes: - appointment_start - (hairdresser_id, appointment_start)

Status values should ultimately be enforced with Django `TextChoices`.

## SQL Assets

Repository contains:

`database/schema.sql`

Purpose: - Rebuild database - Documentation - Version-controlled schema

Next file: `database/seed.sql`

## Existing Django Project

Inherited from an AWS lab.

Current models: - Service - Hairdresser - Appointment

Current Appointment model stores: - customer_contact

Current migrations: - 0001_initial.py - 0002_populate.py

0002_populate.py inserts sample services and hairdressers.

## Important Architectural Decision

The RDS schema has already been redesigned.

Do **not** continue developing against the old schema.

The project should move toward the normalized schema, with Django models
becoming the single source of truth.

## Immediate Tasks

1.  Inspect:

    -   appointments/views.py
    -   appointments/forms.py
    -   appointments/admin.py
    -   appointments/urls.py
    -   templates/

2.  Refactor `appointments/models.py` to include:

    -   Customer
    -   Hairdresser
    -   Service
    -   Appointment

3.  Replace `customer_contact` with `ForeignKey(Customer)`.

4.  Decide on migration strategy:

    -   Rebuild migrations, or
    -   Generate transformation migrations

5.  Connect Django to Amazon RDS.

6.  Configure Django to authenticate using:

    -   `appointment_web_user`
    -   IAM Database Authentication

7.  Create `database/seed.sql` with:

    -   services
    -   hairdressers
    -   customers
    -   appointments

## Design Philosophy

-   Django models are the source of truth.
-   Use Django migrations.
-   Avoid manual schema changes once migrations are established.
-   Keep the database normalized.
-   Business rules belong in Django.
-   Appointment status should use Django `TextChoices`.

## Coding Standards

-   Singular model names
-   Django conventions
-   Default Django `id` primary keys unless justified
-   created_at / updated_at timestamps
-   Readable, maintainable code

## AWS Best Practices

Maintain: - IAM Database Authentication - Least privilege - SSL/TLS -
Dedicated security groups - Low-cost development configuration with
production-oriented architecture

## Long-Term Goals

-   Replace SQLite completely
-   Django uses Amazon RDS
-   IAM-authenticated database connections
-   GitHub → CodeBuild → CodePipeline CI/CD
-   Automated testing
-   Portfolio-quality cloud application
