<<<<<<< HEAD
# Python_Developer_Toolkit
=======
python -m unittest discover -s tests // testing the test class.

# Python Document Processing Toolkit

A robust, concurrent Python application designed to ingest, clean, analyze, and convert multi-format documents (`PDF`, `CSV`, `JSON`, `TXT`) into structured JSON reports.

---

## Features

- **Automatic Format Detection:** Inspects file extensions and dispatches appropriate processing pipelines.
- **Multithreaded Concurrent Execution:** Utilizes `ThreadPoolExecutor` to handle batch processing concurrently for high I/O efficiency.
- **Data Sanitization & Cleaning:** Strips null characters (`\x00`), normalizes extra whitespace, and trims string fields across text, CSVs, and nested JSON structures.
- **Metadata & Statistics Generation:** Computes file-specific metrics (character/word/sentence counts for text/PDFs, row/column info for CSVs, key/item breakdowns for JSON).
- **Structured JSON Exports:** Normalizes extraction outputs into standardized `.json` summaries written to the `output/` directory.
- **Robust Exception Handling & Logging:** Captures runtime errors gracefully without halting the pipeline, logging activity to both stdout and `logs/application.log`.
- **Fully Containerized:** Pre-configured with `Dockerfile` and `docker-compose` for isolated deployment.
- **Comprehensive Unit Testing:** Includes high-coverage unit tests with mocks for external dependencies like `pypdf`.

---

## Project Architecture
                Input Files
                    │
                    ▼
            Detect File Type
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
       PDF         CSV        JSON/TXT
        │           │           │
        └───────────┼───────────┘
                    ▼
            Extract Content
                    │
                    ▼
              Clean Content
                    │
                    ▼
             Generate Stats
                    │
                    ▼
           Structured JSON
                    │
                    ▼
                 Output


100 files
    │
    ▼
ThreadPoolExecutor
    │
    ├── Worker 1 → File
    ├── Worker 2 → File
    ├── Worker 3 → File
    ├── Worker 4 → File
    └── ...
            │
            ▼
       JSON outputs


Dockerfile:

### Option 1: Running with Docker (Recommended)

#### Using Docker Compose
Builds the image and automatically mounts local `input/` and `output/` directories:
```cmd
docker-compose up --build

Using Standard Docker Commands

Build the Docker Image:

Option 1: 
1. docker build -t my_python_document_toolkit .
2. docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" my_python_document_toolkit

Option 2: Running Locally (Windows CMD)
1. Activate Virtual Environment:
2. .myvenv\Scripts\activate

Run Document Processor:
1. python document_toolkit.py
Run Unit Tests:
1. python -m unittest discover -s tests
>>>>>>> 7183ee4 ('Python_document_toolkit')

---

## Git Workflow & Deployment Commands

Follow these steps to initialize, commit, and push changes to the remote GitHub repository:

### 1. Local Commit Workflow
```cmd
# Initialize git in project root (if not already initialized)
git init

# Check the status of untracked/modified files
git status

# Stage all files for commit
git add .

# (Optional) Stage a specific file instead of everything
# git add document_toolkit.py

# Commit staged changes with a descriptive message
git commit -m "feat: complete document processing toolkit implementation"

2. Push Local Changes to Remote GitHub Repository

# Link local repository to remote GitHub URL (run once)
git remote add origin https://github.com/surapuramkamala/Python_Developer_Toolkit.git

# Ensure default branch is named 'main'
git branch -M main

# Pull remote changes first to prevent push rejection conflicts
git pull origin main --rebase

# Push local commits to remote GitHub repository
git push -u origin main or git push -u origin main --force