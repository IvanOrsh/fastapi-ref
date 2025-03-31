## **Quick Guide**

1. Install using pip:

   ```bash
   pip install python-dotenv
   ```

2. Don't forget to `pip freeze > requirements.txt`

3. Load environment variables with:

`./app/__init__.py`:

    ```py
    from dotenv import load_dotenv

    load_dotenv()
    ```
