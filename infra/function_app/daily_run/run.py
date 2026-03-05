"""
Azure Function — Daily Investment Analysis Timer Trigger.

Runs all analyzers daily at 06:00 UTC, uploads reports to Azure Blob Storage,
and triggers a static site rebuild.

Schedule: 0 0 6 * * * (daily at 06:00 UTC)
"""

import datetime
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import azure.functions as func


def main(timer: func.TimerRequest) -> None:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    logging.info(f"Daily analysis triggered at {utc_now.isoformat()}")

    if timer.past_due:
        logging.warning("Timer is past due — running anyway.")

    # Run the orchestrator
    root_dir = Path(__file__).resolve().parents[2]  # infra/function_app -> root
    run_all = root_dir / "run_all.py"

    try:
        result = subprocess.run(
            [sys.executable, str(run_all)],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=600,  # 10 min max
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

        logging.info(f"run_all.py stdout:\n{result.stdout[-2000:]}")
        if result.returncode != 0:
            logging.error(f"run_all.py failed (exit {result.returncode}):\n{result.stderr[-1000:]}")
        else:
            logging.info("Daily analysis completed successfully.")

            # Upload reports to Azure Blob Storage
            upload_reports(root_dir, utc_now.strftime("%Y-%m-%d"))

    except subprocess.TimeoutExpired:
        logging.error("run_all.py timed out after 10 minutes.")
    except Exception as e:
        logging.error(f"Error running daily analysis: {e}")


def upload_reports(root_dir: Path, date: str) -> None:
    """Upload dated reports to Azure Blob Storage."""
    try:
        from azure.storage.blob import BlobServiceClient

        conn_str = os.environ.get("REPORTS_STORAGE_CONNECTION")
        if not conn_str:
            logging.warning("No REPORTS_STORAGE_CONNECTION — skipping upload.")
            return

        blob_service = BlobServiceClient.from_connection_string(conn_str)
        container = blob_service.get_container_client("reports")

        reports_dir = root_dir / "reports" / date
        if not reports_dir.exists():
            logging.warning(f"Reports directory not found: {reports_dir}")
            return

        count = 0
        for file in reports_dir.rglob("*"):
            if file.is_file():
                blob_name = f"{date}/{file.relative_to(reports_dir)}"
                with open(file, "rb") as f:
                    container.upload_blob(blob_name, f, overwrite=True)
                count += 1

        logging.info(f"Uploaded {count} files to blob storage (reports/{date}/)")

    except ImportError:
        logging.warning("azure-storage-blob not installed — skipping upload.")
    except Exception as e:
        logging.error(f"Upload failed: {e}")
