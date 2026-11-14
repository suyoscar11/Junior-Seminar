from __future__ import annotations

import time

from .db import init_db
from .services.publishing import process_due_posts


def main() -> None:
    init_db()
    print("OmniPost scheduler started", flush=True)
    while True:
        processed = process_due_posts()
        if processed:
            print(f"Published {processed} scheduled post(s)", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    main()

