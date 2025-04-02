# **Alembic Commands**

This guide outlines common Alembic commands for managing database migrations.

- **Initialize Alembic:**

  ```bash
  alembic init migrations
  ```

  This command initializes Alembic in the specified directory (`alembic`) with a name (`migrations`).

- **Create initial migration:**

  ```bash
  alembic revision --autogenerate -m "initial"

  alembic -n devdb revision --autogenerate -m "initial"
  ```

  This command generates an initial migration script with automatic detection of changes (`--autogenerate`) and a message (`"initial"`).

- **Upgrade to the latest migration:**

  ```bash
  alembic upgrade head

  alembic -n devdb upgrade head
  ```

  This command applies all migrations up to the latest version (`head`).

- **Execute SQL statement in a migration:**

  ```python
  op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
  ```

  This Python code executes a SQL statement (`CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"`) in a migration.

- **Upgrade to the latest migration with target database:**

  ```bash
  alembic upgrade head -x target_database=engine1
  ```

  This command applies all migrations up to the latest version (`head`) with a target database specified (`engine1`).

- **Create migration with named target database:**

  ```bash
  alembic -n devdb revision --autogenerate -m "Your migration message"
  ```

  This command generates a migration script with a named target database (`engine1`).

- **Upgrade to the latest migration with named target database:**

  ```bash
  alembic -n engine1 upgrade head
  ```

  This command applies all migrations up to the latest version (`head`) with a named target database (`engine1`).

- **Upgrade to the latest migration with another named target database:**

  ```bash
  alembic -n engine2 upgrade head
  ```

  This command applies all migrations up to the latest version (`head`) with another named target database (`engine2`).
