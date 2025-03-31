# **Uvicorn Command Reference**

- **Commands**

  ```bash
  uvicorn app.main:app --reload
  ```

  This command is used to run a FastAPI app using the UVicorn ASGI server with auto-reload enabled.

  **Arguments:**

  - `app.main:app`: Specifies the Python module and ASGI application instance to run. In ths example, `app` refers to the FastAPI application instance withing the `main` module.
  - `--reload`: Enables auto-reload functionality, causing the server to restart whenever the source code changes.

  **Usage**

  - Run the command in the terminal to start the FastAPI application with UVicorn and auto-reload functionality.
