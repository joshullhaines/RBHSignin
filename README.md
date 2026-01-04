# RBH Sign In / Sign Out (RBHSignin)

This is a small PyQt app. The primary setup below is **Windows (PowerShell)**.

## Why do we use a `.venv`?

We use a virtual environment (`.venv`) so that:
- **Dependencies are isolated** to this project (no global Python pollution).
- **Everyone installs the same packages** (fewer “works on my machine” issues).
- **Cursor/VS Code can reliably find the interpreter** inside the repo and resolve imports.

## Windows setup (PowerShell) — recommended

### 0) Verify Python 3.13 is available

```powershell
py -3.13 --version
```

### 1) Create a virtual environment (one-time)

```powershell
py -3.13 -m venv .venv
```

### 2) Activate it (every new terminal)

```powershell
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4) Run the app

```powershell
python RBH_volunteersplash.py
```

## Troubleshooting (Windows)

### Activation is blocked (ExecutionPolicy)

If you see an error about scripts being disabled, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run activation again:

```powershell
.venv\Scripts\Activate.ps1
```

### `py -3.13` not found

- Install **Python 3.13** for Windows and ensure the **Python Launcher** (`py`) is installed.
- Quick check of installed Python versions:

```powershell
py -0p
```

## Notes

- **`Information.db`** is the local SQLite database used by the app and is treated as the current source of truth.
  - It contains personal fields (name/email/address/phone). Please be mindful about sharing it and avoid committing accidental changes.
- **`dbprep.py`** is a helper script that drops/recreates some tables (use carefully).

## macOS/Linux (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python RBH_volunteersplash.py
```


