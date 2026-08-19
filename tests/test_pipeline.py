import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from document_toolkit import (
    PdfReader,
    clean_csv,
    clean_json,
    clean_text,
    csv_statistics,
    detect_file_type,
    discover_files,
    json_statistics,
    process_pdf,
    text_statistics,
)

class TestDocumentProcessingPipeline(unittest.TestCase):

    # ----------------------------------------------------
    # 1. FILE TYPE DETECTION TESTS
    # ----------------------------------------------------
    def test_detect_file_type_valid(self):
        self.assertEqual(detect_file_type(Path("sample.pdf")), "pdf")
        self.assertEqual(detect_file_type(Path("data.csv")), "csv")
        self.assertEqual(detect_file_type(Path("config.json")), "json")
        self.assertEqual(detect_file_type(Path("notes.txt")), "txt")

    def test_detect_file_type_invalid(self):
        with self.assertRaises(ValueError):
            detect_file_type(Path("image.png"))

    # ----------------------------------------------------
    # 2. CONTENT CLEANING TESTS
    # ----------------------------------------------------
    def test_clean_text(self):
        raw_text = "  Hello \x00 world!   This   is a   test. \n\n "
        expected = "Hello world! This is a test."
        self.assertEqual(clean_text(raw_text), expected)

    def test_clean_csv(self):
        raw_data = [{"name": "  Alice \x00 ", "age": "30"}]
        expected = [{"name": "Alice", "age": "30"}]
        self.assertEqual(clean_csv(raw_data), expected)

    def test_clean_json(self):
        raw_data = {"user": "  Kalya   ", "items": [" item1 ", " item2 \x00 "]}
        expected = {"user": "Kalya", "items": ["item1", "item2"]}
        self.assertEqual(clean_json(raw_data), expected)

    # ----------------------------------------------------
    # 3. STATISTICS TESTS
    # ----------------------------------------------------
    def test_text_statistics(self):
        text = "Hello world. This is a test!"
        stats = text_statistics(text)
        self.assertEqual(stats["words"], 6)
        self.assertEqual(stats["sentences"], 2)

    def test_csv_statistics(self):
        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        stats = csv_statistics(data)
        self.assertEqual(stats["rows"], 2)
        self.assertEqual(stats["columns"], 2)
        self.assertIn("name", stats["column_names"])

    def test_json_statistics(self):
        data = {"key1": "val1", "key2": "val2"}
        stats = json_statistics(data)
        self.assertEqual(stats["data_type"], "object")
        self.assertEqual(stats["keys"], 2)

    # ----------------------------------------------------
    # 4. FILE PROCESSOR MOCK TESTS
    # ----------------------------------------------------
    @patch.object(PdfReader, "__new__")
    def test_process_pdf(self, mock_reader_cls):
        mock_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Extracted PDF content."
        mock_instance.pages = [mock_page]
        mock_reader_cls.return_value = mock_instance

        result = process_pdf(Path("dummy.pdf"))
        self.assertEqual(result, "Extracted PDF content.")
    
    # ----------------------------------------------------
    # 5. DISCOVER & SAVE TESTS
    # ----------------------------------------------------
    def test_discover_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            (dir_path / "doc1.pdf").touch()
            (dir_path / "data.csv").touch()
            (dir_path / "ignored.exe").touch()

            discovered = discover_files(dir_path)
            filenames = [f.name for f in discovered]

            self.assertEqual(len(discovered), 2)
            self.assertIn("doc1.pdf", filenames)
            self.assertIn("data.csv", filenames)
            self.assertNotIn("ignored.exe", filenames)
"""
    # ----------------------------------------------------
    # 6. FAILURE SCENARIO TESTS
    # ----------------------------------------------------
    def test_process_file_missing_file(self):
        #Test handling of non-existent files.
        result = process_file(Path("non_existent_file.txt"))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"], "File not found")

    def test_process_file_corrupt_json(self):
        #Test handling of invalid/corrupt JSON structure.
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_json_path = Path(temp_dir) / "corrupt.json"
            bad_json_path.write_text("{ invalid json syntax ...", encoding="utf-8")

            result = process_file(bad_json_path)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["error"], "Invalid JSON format")

    def test_discover_files_missing_directory(self):
        #Test file discovery on a non-existent folder.
        with self.assertRaises(FileNotFoundError):
            discover_files(Path("missing_folder_xyz"))
            """


if __name__ == "__main__":
    unittest.main()