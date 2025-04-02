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
