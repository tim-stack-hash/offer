"""Run the existing bot with Telegram content protection enabled.

Start this file instead of main.py to prevent users from forwarding or
copying messages and media sent by the bot through Telegram's built-in UI.
"""

import main
from telegram.ext import Application, Defaults


_original_builder = Application.builder


def _protected_builder():
    """Build the application with protected content as the default."""
    return _original_builder().defaults(Defaults(protect_content=True))


# Keep the existing main.py untouched while applying the setting to the
# Application built inside main.main().
Application.builder = staticmethod(_protected_builder)


if __name__ == "__main__":
    main.main()
