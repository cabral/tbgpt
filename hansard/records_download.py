from selenium import webdriver
from datetime import datetime, timedelta
import time
import os


def download_pdfs(start_date, end_date, download_folder):
    base_url = "https://hansard.parliament.uk/pdf/commons/"

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
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        while current_date <= end_date:
            url = base_url + current_date.strftime("%Y-%m-%d")
            driver.get(url)

            # Wait for a short duration to ensure the PDF starts downloading
            time.sleep(5)

            print(f"Attempted to download PDF for {current_date.strftime('%Y-%m-%d')}")

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
