import csv
import json
import logging #logging is used to record what application is doing.
import re  #regular expression. It is commonly used for cleaning text.
from concurrent.futures import ThreadPoolExecutor, as_completed #These are used for parallel file processing. Without threading, you might process them one by one:
from pathlib import Path #Path is used for working with files and folders.
from typing import Any #Any is used for type hints

from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")

SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".csv": "csv",
    ".json": "json",
    ".txt": "txt",
}


# ============================================================
# LOGGING
# ============================================================

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s", # level means like info or WARNING or error
    handlers=[
        logging.FileHandler(LOG_DIR / "application.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# FILE TYPE DETECTION
# ============================================================

def detect_file_type(file_path: Path) -> str:

    extension = file_path.suffix.lower() # Takes a file path, extracts its lowercase extension using .suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return SUPPORTED_EXTENSIONS[extension] # Returns the normalized file type name


# ============================================================
# PDF PROCESSOR
# ============================================================

def process_pdf(file_path: Path) -> str: #This function extracts raw text from a PDF document page. pypdf.PdfReader and returns it as a single combined string.

    logger.info("Reading PDF: %s", file_path.name)

    reader = PdfReader(str(file_path))

    pages = []

    for page in reader.pages:

        text = page.extract_text() or ""

        pages.append(text)

    return "\n".join(pages)


# ============================================================
# TXT PROCESSOR
# ============================================================

def process_txt(file_path: Path) -> str:

    logger.info("Reading TXT: %s", file_path.name)

    with open(
        file_path,
        "r",
        encoding="utf-8" #encoding="utf-8" ensures standard character formatting (like accented letters or emojis) reads correctly.
    ) as file:

        return file.read()


# ============================================================
# CSV PROCESSOR
# ============================================================

def process_csv(file_path: Path) -> list:

    logger.info("Reading CSV: %s", file_path.name)

    with open(
        file_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file) #it reads the top header row and converts each subsequent data row into a dictionary where the keys are the column names.
        return list(reader)


# ============================================================
# JSON PROCESSOR
# ============================================================

def process_json(file_path: Path) -> Any:

    logger.info("Reading JSON: %s", file_path.name)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# CONTENT CLEANING
# ============================================================

def clean_text(text: str) -> str:

    if not isinstance(text, str):
        return text

    # Remove null characters
    text = text.replace("\x00", "")

    # Replace multiple spaces/newlines with one space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def clean_csv(data: list) -> list:

    cleaned_data = []

    for row in data:

        cleaned_row = {}

        for key, value in row.items():

            if isinstance(value, str):
                cleaned_row[key] = clean_text(value)
            else:
                cleaned_row[key] = value

        cleaned_data.append(cleaned_row)

    return cleaned_data


def clean_json(data: Any) -> Any:

    if isinstance(data, dict):

        return {
            key: clean_json(value)
            for key, value in data.items()
        }

    if isinstance(data, list):

        return [
            clean_json(item)
            for item in data
        ]

    if isinstance(data, str):

        return clean_text(data)

    return data


# ============================================================
# STATISTICS
# ============================================================

def text_statistics(text: str) -> dict:

    words = text.split()

    sentences = re.findall(
        r"[.!?]+",
        text
    )

    return {
        "characters": len(text),
        "words": len(words),
        "lines": len(text.splitlines()),
        "sentences": len(sentences),
    }


def csv_statistics(data: list) -> dict:

    if not data:

        return {
            "rows": 0,
            "columns": 0,
            "column_names": []
        }

    return {
        "rows": len(data),
        "columns": len(data[0]),
        "column_names": list(data[0].keys())
    }


def json_statistics(data: Any) -> dict:

    if isinstance(data, dict):

        return {
            "data_type": "object",
            "keys": len(data),
            "key_names": list(data.keys())
        }

    if isinstance(data, list):

        return {
            "data_type": "array",
            "items": len(data)
        }

    return {
        "data_type": type(data).__name__
    }


# ============================================================
# PROCESS ONE FILE
# ============================================================

def process_file(file_path: Path) -> dict:

    logger.info(
        "Starting processing: %s",
        file_path.name
    )

    try:

        # ----------------------------------------------------
        # 1. Detect file type
        # ----------------------------------------------------

        file_type = detect_file_type(file_path)

        logger.info(
            "Detected type: %s",
            file_type
        )

        # ----------------------------------------------------
        # 2. Extract content
        # ----------------------------------------------------

        if file_type == "pdf":

            content = process_pdf(file_path)

        elif file_type == "txt":

            content = process_txt(file_path)

        elif file_type == "csv":

            content = process_csv(file_path)

        elif file_type == "json":

            content = process_json(file_path)

        else:

            raise ValueError(
                f"Unsupported type: {file_type}"
            )

        # ----------------------------------------------------
        # 3. Clean content
        # ----------------------------------------------------

        if file_type in ["pdf", "txt"]:

            cleaned_content = clean_text(content)

        elif file_type == "csv":

            cleaned_content = clean_csv(content)

        elif file_type == "json":

            cleaned_content = clean_json(content)

        # ----------------------------------------------------
        # 4. Generate statistics
        # ----------------------------------------------------

        if file_type in ["pdf", "txt"]:

            statistics = text_statistics(
                cleaned_content
            )

        elif file_type == "csv":

            statistics = csv_statistics(
                cleaned_content
            )

        elif file_type == "json":

            statistics = json_statistics(
                cleaned_content
            )

        # ----------------------------------------------------
        # 5. Create structured output
        # ----------------------------------------------------

        result = {
            "file_name": file_path.name,
            "file_type": file_type,
            "status": "success",
            "statistics": statistics,
            "content": cleaned_content
        }

        logger.info(
            "Successfully processed: %s",
            file_path.name
        )

        return result

    except FileNotFoundError:

        logger.error(
            "File not found: %s",
            file_path
        )

        return {
            "file_name": file_path.name,
            "status": "failed",
            "error": "File not found"
        }

    except PermissionError:

        logger.error(
            "Permission denied: %s",
            file_path
        )

        return {
            "file_name": file_path.name,
            "status": "failed",
            "error": "Permission denied"
        }

    except json.JSONDecodeError:

        logger.exception(
            "Invalid JSON: %s",
            file_path.name
        )

        return {
            "file_name": file_path.name,
            "status": "failed",
            "error": "Invalid JSON format"
        }

    except Exception as e:

        logger.exception(
            "Unexpected error processing %s",
            file_path.name
        )

        return {
            "file_name": file_path.name,
            "status": "failed",
            "error": str(e)
        }


# ============================================================
# DISCOVER FILES ->`discover_files` is a utility function that scans a specified folder directory, 
# filters out unsupported formats, and returns a clean list of valid file paths ready for processing.
# ============================================================

def discover_files(directory: Path) -> list[Path]:

    if not directory.exists():

        raise FileNotFoundError(
            f"Input directory does not exist: {directory}"
        )

    files = []

    for file_path in directory.iterdir():

        if file_path.is_file():

            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:

                files.append(file_path)

    return files


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(result: dict):

    OUTPUT_DIR.mkdir(exist_ok=True)

    file_name = result["file_name"]

    output_file = (
        OUTPUT_DIR /
        f"{Path(file_name).stem}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Output saved: %s",
        output_file
    )


# ============================================================
# PROCESS MULTIPLE FILES CONCURRENTLY
# ============================================================

def process_all_files(files: list[Path]):

    results = []

    logger.info(
        "Processing %d files",
        len(files)
    )

    # ThreadPoolExecutor is suitable here
    # because file processing involves I/O operations.

    with ThreadPoolExecutor(
        max_workers=4
    ) as executor:

        future_to_file = {
            executor.submit(
                process_file,
                file_path
            ): file_path

            for file_path in files
        }

        for future in as_completed(
            future_to_file
        ):

            file_path = future_to_file[future]

            try:

                result = future.result()

                results.append(result)

                save_result(result)

            except Exception:

                logger.exception(
                    "Failed processing: %s",
                    file_path
                )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 60)
    logger.info("Python Document Processing Toolkit")
    logger.info("=" * 60)

    try:

        # Discover input files
        files = discover_files(
            INPUT_DIR
        )

        if not files:

            logger.warning(
                "No supported files found in %s",
                INPUT_DIR
            )

            return

        logger.info(
            "Found %d supported files",
            len(files)
        )

        # Process all files
        results = process_all_files(
            files
        )

        # Summary
        successful = sum(
            1
            for result in results
            if result["status"] == "success"
        )

        failed = len(results) - successful

        logger.info("=" * 60)
        logger.info(
            "Processing completed"
        )
        logger.info(
            "Successful: %d",
            successful
        )
        logger.info(
            "Failed: %d",
            failed
        )
        logger.info("=" * 60)

    except Exception:

        logger.exception(
            "Application failed"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()