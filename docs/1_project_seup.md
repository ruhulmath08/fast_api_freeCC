# FastAPI project step by step

1. Creates an isolated Python virtual environment
2. Use the virtual environment
3. Use the virtual environment interpreter
4. Install FastAPI
5. Run the server

## 1. Creates an isolated Python virtual environment

```bash
python3 -m venv .venv
```

creates an isolated Python environment in a `.venv` folder so project packages stay separate from the system Python.

## 2. Use the virtual environment

```bash
source .venv/bin/activate
```

activates the virtual environment so the project packages are used instead of the system Python.

## 3. Use the virtual environment interpreter

Go to `View > Command Palette > Python: Select Interpreter > ./.venv/bin/python`

## 4. Install FastAPI

```bash
pip install "fastapi[standard]"
```

installs the FastAPI package.

## 5. Run the server

```bash
uvicorn main:app --reload
```

runs the server so you can see the API in the browser.
