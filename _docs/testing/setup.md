## TODO: requires some work, very chaotic

## What we are trying to achieve?

Run tests:

1. Create Test Container (docker test-db container, programmatically)
2. Integrate `alembic` **migrations**
3. Insert data into db (fixtures)
4. Actual testing
5. Clean up (programmatically remove docker test-db container)

## How are we going to achieve this?

When we run `pytest ...` command:

1. It's going to hit `conftest.py`, that

   - Is going to use **fixture** (`./tests/fixtures.py`)
     - For the entire session (testing session):
       - we will create a docker db container

2. Then, it will start running tests.

3. Once the tests are completed, container are going to be stopped and removed.

## Steps:

1. `pip install pytest-alembic`

   - This will install `pytest` and `pytest-alembic`, which provides easy integrations with `pytest` and `alembic`.
   - don't forget `pip freeze > requirements.txt`

2. create `pytest.ini` to configure `pytest`

   ```ini
   [pytest]
   testpaths=tests

   ```

3. Place `tests` folder inside root dir (for now\_).

   - Don't forget about putting `__init__.py` inside `./tests`

4. Inside `tests` create `conftest.py`:

   - A special configuration file that allows you to define fixtures, hooks, and custom configurations for your test suite. It is automatically detected by pytest and does not require explicit imports in your test files.

5. `pytest -s`

6. Create a Docker Test Database Programmatically:

   1. `pip install docker`
   2. Inside `./tests/utils/docker_utils.py`:

   ```py
    import os
    import platform
    import time

    import docker
    import docker.errors


    def is_container_ready(container):
        container.reload()
        return container.status == "running"


    def wait_for_stable_status(container, stable_duration=3, interval=1):
        start_time = time.time()
        stable_count = 0
        while time.time() - start_time < stable_duration:
            if is_container_ready(container):
                stable_count += 1
            else:
                stable_count = 0

            if stable_count >= stable_duration / interval:
                return True

            time.sleep(interval)
        return False


    def get_docker_client():
        system = platform.system()

        # Default Unix/Linux/Mac socket
        linux_socket = "/var/run/docker.sock"
        desktop_socket = os.path.expanduser("~/.docker/desktop/docker.sock")

        # Windows named pipe
        windows_pipe = "npipe:////./pipe/docker_engine"

        if system == "Windows":
            return docker.DockerClient(base_url=windows_pipe)
        elif os.path.exists(linux_socket):
            return docker.DockerClient(base_url=f"unix://{linux_socket}")
        elif os.path.exists(desktop_socket):
            return docker.DockerClient(base_url=f"unix://{desktop_socket}")
        else:
            raise RuntimeError("No valid Docker socket or pipe found!")


    def start_database_container():
        # client = docker.from_env()
        client = get_docker_client()
        # print(client.containers.list())
        scripts_dir = os.path.abspath("./scripts")
        container_name = "test-db"

        try:
            existing_container = client.containers.get(container_name)
            print(f"Container '{container_name} exists. Stopping and removing...")
            existing_container.stop()
            existing_container.remove()
            print(f"Container '{container_name}' stopped and removed.")
        except docker.errors.NotFound:
            print(f"Container '{container_name}' does not exists.")

        # Define container configuration
        container_config = {
            "name": container_name,
            "image": "postgres:16.1-alpine3.19",
            "detach": True,
            "ports": {"5432": "5434"},
            "environment": {
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
            },
            "volumes": [f"{scripts_dir}:/docker-entrypoint-initdb.d"],
            "network_mode": "fastapi-development_dev-network",
        }

        container = client.containers.run(**container_config)

        while not is_container_ready(container):
            time.sleep(1)

        if not wait_for_stable_status(container):
            raise RuntimeError("Container did not stabilize within the specified time.")

        return container


   ```

   3. Create `./tests/fixtures.py`:

   ```py
    import pytest

    from tests.utils.docker_utils import start_database_container


    @pytest.fixture(scope="session", autouse=True)
    def db_session():
        container = start_database_container()

   ```

7. To test our setup quickly:

   1. `./tests/models/test_new.py`:

   ```py
   def test_condition_is_true():
        assert True
   ```

8. Now we Configure `alembic` for multi-databases:

   1. Add `testdb`to `./alembic.ini`:

   ```ini
    [alembic]

    [devdb]

    script_location = migrations
    prepend_sys_path = .
    version_path_separator = os
    sqlalchemy.url =

    [testdb]

    script_location = migrations
    prepend_sys_path = .
    version_path_separator = os
    sqlalchemy.url =

   ```

   2. Edit `.env`: Add `TEST_DATABASE_URL`:

   ```.env
    DEV_DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/inventory
    TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5434/inventory
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
   ```

   3. Edit `./migrations/env.py`

   ```py
   # ...

   config = context.config

   if config.config_file_name is not None:
       fileConfig(config.config_file_name)

   # Set the database URLs based on environment variables or any other source
   url_devdb = os.environ.get("DEV_DATABASE_URL")
   url_testdb = os.environ.get("TEST_DATABASE_URL")

   # Modify the database URLs in the Alembic config
   config.set_section_option("devdb", "sqlalchemy.url", url_devdb)
   config.set_section_option("testdb", "sqlalchemy.url", url_testdb)

   # ...
   ```

   4. Now we need utility function to perform migrations: `./tests/utils/database_utils.py`:

   ```py
    import alembic.config
    from alembic import command


    def migrate_to_db(
        script_location, alembic_ini_path="alembic.ini", connection=None, revision="head"
    ):
        config = alembic.config.Config(alembic_ini_path)
        if connection is not None:
            config.config_ini_section = "testdb"
            command.upgrade(config, revision)

   ```

   5. Now edit our `./tests/fixture.py` to make use of `migrate_to_db` from `database_utility.py`:

   ```py
    import pytest
    import os
    from sqlalchemy import create_engine

    from tests.utils.docker_utils import start_database_container
    from tests.utils.database_utils import migrate_to_db


    @pytest.fixture(scope="session", autouse=True)
    def db_session():
        container = start_database_container()

        engine = create_engine(os.getenv("TEST_DATABASE_URL"))

        with engine.begin() as connection:
            migrate_to_db("migrations", "alembic.ini", connection)
   ```

9. Now we need to remove containers after testing
