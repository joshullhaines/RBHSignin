# Written by Josh Hull-Haines on 2025 to create a SISO Application for RBH
#
# NOTE (2026): The app code has been split into modules under `rbh_siso/` to make it easier
# to maintain and to prepare for an upcoming DB/schema redesign. This file is intentionally
# kept as a thin entrypoint for backwards compatibility (README, PyInstaller spec, etc.).
#
# Where did things go?
# - Main menu dialog: `rbh_siso/ui/main_dialog.py` (RBHSISO)
# - Volunteer dialogs: `rbh_siso/ui/volunteer_dialogs.py`
# - Client dialogs: `rbh_siso/ui/client_dialogs.py`
# - Activity dialogs: `rbh_siso/ui/activity_dialogs.py`
# - Shared UI widgets: `rbh_siso/ui/common.py`
# - App entrypoint: `rbh_siso/app.py`

from rbh_siso.app import main


if __name__ == "__main__":
	main()


