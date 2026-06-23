import io
from pathlib import Path

invoice_ai_dir_path = Path(__file__).parent.parent

env_rows = ["# Api keys", "OPENROUTER_API_KEY", "\n", "# DB Properties", "DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME"]

with io.open(str(invoice_ai_dir_path / "test.env"), "w") as file:
    for row in env_rows:
        if row.startswith("#") or row.startswith("\n"):
            file.write(row + "\n")
        else:
            file.write(row + "=" + "\n")
