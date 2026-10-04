# COMPRO Group Project

This project is a Python desktop application built with Flet. It is designed to run locally on a personal computer and includes the app source code, UI files, assets, and project data needed to launch the program.

If you receive the project as a ZIP file, simply extract the folder to a location on your computer, open a terminal in that folder, install the Python dependencies, and run the app.

---

## 1. Requirements

Before running the project, make sure your computer has:

- Python 3.10 or newer
- pip (usually included with Python)
- A terminal or PowerShell window
- A Windows 10/11 computer is recommended for this project

You can check your Python version with:

```powershell
python --version
```

If `python` does not work, try:

```powershell
py --version
```

---

## 2. Extract the project

If the project was sent as a ZIP file:

1. Extract the ZIP file to a folder such as:
   ```text
   C:\Users\YourName\Desktop\COMPRO_group_proj
   ```
2. Make sure the extracted folder contains files like:
   - `main.py`
   - `requirements.txt`
   - `app/`
   - `ui/`
   - `assets/`
   - `seed/`

---

## 3. Open a terminal in the project folder

Open PowerShell in the extracted folder.

You can do this by:

- Opening PowerShell and using `cd`
- Or right-clicking inside the folder and selecting "Open in Terminal" if available

Example:

```powershell
cd C:\Users\YourName\Desktop\COMPRO_group_proj
```

---

## 4. Create a virtual environment (recommended)

This keeps the project dependencies isolated from the rest of your Python setup.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

---

## 5. Install the dependencies

From the project root, run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project already includes the required packages in `requirements.txt`.

---

## 6. Run the project

From the project root, start the app with:

```powershell
python main.py
```

If your system uses `py` instead of `python`, use:

```powershell
py main.py
```

The app should open as a desktop Flet application.

---

## 7. Project structure overview

This project is organized as follows:

```text
COMPRO_group_proj/
├── main.py                 # App entry point
├── requirements.txt        # Python dependencies
├── save.json               # Local save data
├── app/                    # Core application logic
├── ui/                     # User interface screens and views
├── assets/                 # Images, audio, buttons, sprites, etc.
├── seed/                   # Seed data, such as species information
├── build/                  # Generated build artifacts
├── Documentation/          # Project documentation/specs
└── README.md               # Setup and usage guide
```

---

## 8. Notes for running from a ZIP file

When the project is sent as a ZIP archive, the receiver should:

- Extract the full folder, not just a few files
- Keep the folder structure intact
- Run the app from the project root, not from inside a subfolder
- Ensure `assets/` and `seed/` are not missing
- Install dependencies from `requirements.txt`

If any images, sounds, or data do not load, check that the project was fully extracted and that the folder structure still matches the original layout.

---

## 9. Before sending the project to your professor

Use this checklist before submitting:

- [ ] Project runs on a fresh computer after extracting the ZIP file
- [ ] `requirements.txt` includes all required libraries
- [ ] No personal data, local paths, or usernames are left in the code
- [ ] No debug print statements or temporary testing code remain
- [ ] Unused files and generated folders are removed if not needed
- [ ] `__pycache__`, `.venv`, and build output folders are not included unless required
- [ ] The project contains a clear `README.md` with setup instructions
- [ ] All imports are valid and there are no obvious missing dependencies
- [ ] Save data or local state is not incorrectly shipped as project content unless intended
- [ ] The code is organized and readable, with consistent naming and comments only where necessary

---

## 10. Recommended cleanup before final submission

Before sending the final ZIP to your professor, it is good to do the following:

1. Delete local virtual environments such as `.venv`
2. Remove generated cache folders such as `__pycache__`
3. Delete temporary logs or local saves if they are not part of the project design
4. Make sure the app still runs after a clean reinstall
5. Keep only the files that are needed for the project to work
6. Confirm that the project is easy for someone else to run without extra setup steps

A clean project should be easy to unzip, install, and run without needing hidden files or extra manual changes.

---

## 11. Final reminder

If you send the project in a ZIP file, the easiest way for a professor or reviewer to run it is:

```powershell
cd path\to\extracted\folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

This is the simplest local setup flow for a Windows machine.
