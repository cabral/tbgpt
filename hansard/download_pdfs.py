from selenium import webdriver
from datetime import datetime, timedelta
import time
import os


def download_pdf(url, download_folder):
    """Downloads a PDF file to the specified download folder.

    Args:
      url: The URL of the PDF file to download.
      download_folder: The path to the download folder.
    """

    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        },
    )

    with webdriver.Chrome(options=options) as driver:
        driver.get(url)

        # Wait for a short duration to ensure the PDF starts downloading
        time.sleep(5)

        # Move to the next date


def download_pdfs(start_date, end_date, download_folder):
    """Downloads PDF files for a given date range to the specified download folder.

    Args:
      start_date: The start date for the date range (YYYY-MM-DD).
      end_date: The end date for the date range (YYYY-MM-DD).
      download_folder: The path to the download folder.
    """

    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date:
        url = f"https://hansard.parliament.uk/pdf/commons/{current_date.strftime('%Y-%m-%d')}"

        download_pdf(url, download_folder)

        # Move to the next date
        current_date += timedelta(days=1)


if __name__ == "__main__":
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    download_folder = input(
        "Enter the path to the download folder (e.g., /path/to/folder): "
    )

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    download_pdfs(start_date, end_date, download_folder)
