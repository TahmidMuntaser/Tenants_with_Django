# Tenants_with_Django

Learning **Multi-Tenant SaaS Development with Django** from scratch. This repository documents my learning journey as I explore the fundamentals of schema-based multi-tenancy using **django-tenants**, implement concepts step by step, and build practical projects along the way.

---

# Tenant Manager Setup

This project uses **django-tenants** to implement **schema-based multi-tenancy** with PostgreSQL. Instead of creating a separate database for every client, each tenant gets its own PostgreSQL **schema**, providing complete data isolation while sharing the same database.

## Models (`a_tenant_manager/models.py`)

The tenant manager defines two models:

### Tenant (`TenantMixin`)

* Represents a client or organization.
* Stores tenant information such as its name and creation time.
* Each tenant is associated with its own PostgreSQL schema.

### Domain (`DomainMixin`)

* Maps a domain (or subdomain) to a tenant.
* Used by **django-tenants** to identify which tenant should handle an incoming request.

---

## Configuration (`_core/settings.py`)

### Shared Apps vs Tenant Apps

Applications are divided into two groups to determine where their database tables are created.

| Category        | Purpose                                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| **SHARED_APPS** | Installed only in the **public schema**. These applications store shared data used across the entire system. |
| **TENANT_APPS** | Installed inside every tenant schema. Each tenant gets its own copy of these tables and data.                |

`INSTALLED_APPS` is created by combining both lists while automatically removing duplicate entries.

---

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)
```

#### Explanation

* Uses `django_tenants.postgresql_backend` to enable schema-based multi-tenancy.
* `TenantSyncRouter` determines whether migrations should run in the **public schema** or in **tenant schemas**, ensuring each application is migrated to the correct schema.

---

### Middleware

```python
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    ...
]
```

`TenantMainMiddleware` **must be the first middleware** in the middleware list.

It inspects the incoming request's domain, identifies the corresponding tenant, and automatically switches the database connection to that tenant's PostgreSQL schema before the request is processed.

---

### Tenant Configuration

```python
TENANT_MODEL = "a_tenant_manager.Tenant"
TENANT_DOMAIN_MODEL = "a_tenant_manager.Domain"

SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

PUBLIC_SCHEMA_URLCONF = "_core.urls_public"
```

#### Explanation

* `TENANT_MODEL` specifies the model representing tenants.
* `TENANT_DOMAIN_MODEL` specifies the model used for domain-to-tenant mapping.
* `SHOW_PUBLIC_IF_NO_TENANT_FOUND = True` serves the **public schema** whenever no tenant matches the incoming domain.
* `PUBLIC_SCHEMA_URLCONF` specifies a dedicated URL configuration for the public schema.

The **public schema** contains the applications listed in `SHARED_APPS`, while each tenant schema contains only the applications listed in `TENANT_APPS`.

---

## Public Schema URLs (`_core/urls_public.py`)

The project now uses a dedicated URL configuration for the **public schema**.

The public URL configuration includes:

* `admin/` — Default Django admin
* `admin_tenants/` — Custom Tenant Admin
* `accounts/` — Authentication with **django-allauth**
* `/` — Home page
* `create-item/` — Create item page
* `profile/` — User profile URLs
* `@<username>/` — Public user profile pages

During development it also serves:

* Media files
* django-browser-reload

---

## Custom Tenant Admin (`a_tenant_manager/admin.py`)

A dedicated admin site has been created to manage tenants separately from the default Django admin.

```python
tenant_admin_site = TenantAdminSite(name="tenant_admin")
```

This admin site automatically registers:

* `Tenant`
* `Domain`

Benefits:

* Dedicated interface for tenant management.
* Keeps tenant administration separate from application administration.
* Simplifies managing tenants and their domains.

Accessible at:

```
/admin_tenants/
```

---

## Dynamic Tenant Branding

The application header now displays the active tenant's name dynamically.

If `request.tenant` exists:

```django
{{ request.tenant.name }}
```

Otherwise, it falls back to:

```
Django Tenants
```

This makes it easy to identify the currently active tenant.

---

## Docker Setup (`docker-compose.yml`)

```yaml
services:
  postgres:
    image: postgres:17
    container_name: postgres-container

    ports:
      - "5433:5432"

    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

    volumes:
      - postgres-data:/var/lib/postgresql/data
```

#### Explanation

* PostgreSQL **17** runs inside a Docker container.
* Container port **5432** is mapped to host port **5433** because another PostgreSQL instance already uses port **5432** on the host machine.
* Connect using:

```text
Host: localhost
Port: 5433
Database: postgres
Username: postgres
Password: postgres
```

* The `postgres-data` volume persists the database even if the container is recreated.

---

## Running Migrations

Create the tables in the **public schema**:

```bash
python manage.py migrate_schemas --shared
```

Apply migrations to every tenant schema:

```bash
python manage.py migrate_schemas
```

---

# Creating a Tenant

Create a new tenant using the custom management command:

```bash
python manage.py create_tenant
```

You will be prompted to enter:

| Field           | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| **Schema Name** | Name of the PostgreSQL schema that will be created for the tenant.        |
| **Name**        | Display name of the tenant or organization.                               |
| **Domain**      | Domain or subdomain used to access the tenant (e.g. `tenant1.localhost`). |
| **Is Primary**  | Indicates whether this is the tenant's primary domain.                    |

After the command completes:

* A new PostgreSQL schema is created.
* A `Tenant` record is created.
* A corresponding `Domain` record is created.
* The tenant is ready to receive requests through its configured domain.

---

# Creating a Tenant Superuser

Each tenant has its own authentication tables and administrator accounts.

Create a tenant superuser using:

```bash
python manage.py create_tenant_superuser
```

You will be prompted to enter:

| Field             | Description                                   |
| ----------------- | --------------------------------------------- |
| **Tenant Schema** | Schema where the superuser should be created. |
| **Username**      | Superuser username.                           |
| **Email**         | Superuser email address.                      |
| **Password**      | Superuser password.                           |

The created superuser has administrative access only within the specified tenant schema.

---

## Project Structure

```text
Tenants_with_Django/
│
├── _core/
│   ├── settings.py
│   └── urls_public.py
|   └── urls.py        
│
├── a_tenant_manager/
│   ├── admin.py
│   └── models.py
│
├── a_home/
├── a_users/
├── templates/
├── docker-compose.yml
├── manage.py
└── README.md
```
