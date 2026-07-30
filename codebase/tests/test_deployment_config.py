import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

import _bootstrap  # noqa: F401

from app import load_runtime_secrets


CODEBASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CODEBASE_DIR.parent


class DeploymentConfigTest(unittest.TestCase):
    def test_load_runtime_secrets_handles_missing_st_secrets_safely(self):
        with patch("app.st", object()):  # object has no `secrets` attribute
            try:
                load_runtime_secrets()
            except Exception as error:
                self.fail(f"load_runtime_secrets raised an unexpected exception: {error}")

    def test_load_runtime_secrets_does_not_overwrite_existing_env(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "existing_env_key"}, clear=True):
            mock_st = MagicMock()
            mock_st.secrets = {"GEMINI_API_KEY": "secret_key_from_st"}

            with patch("app.st", mock_st):
                load_runtime_secrets()

            self.assertEqual(os.environ.get("GEMINI_API_KEY"), "existing_env_key")

    def test_load_runtime_secrets_populates_missing_env(self):
        with patch.dict(os.environ, {}, clear=True):
            mock_st = MagicMock()
            mock_st.secrets = {
                "GEMINI_API_KEY": "secret_key_123",
                "GEMINI_MODEL": "gemini-3.5-flash-lite",
                "ASSISTANT_DB_PATH": "data/test.db",
            }

            with patch("app.st", mock_st):
                load_runtime_secrets()

            self.assertEqual(os.environ.get("GEMINI_API_KEY"), "secret_key_123")
            self.assertEqual(os.environ.get("GEMINI_MODEL"), "gemini-3.5-flash-lite")
            self.assertEqual(os.environ.get("ASSISTANT_DB_PATH"), "data/test.db")

    def test_load_runtime_secrets_does_not_print_or_log_secrets(self):
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()

        with patch.dict(os.environ, {}, clear=True):
            mock_st = MagicMock()
            mock_st.secrets = {"GEMINI_API_KEY": "SUPER_SECRET_KEY_999"}

            with patch("sys.stdout", captured_stdout), patch("sys.stderr", captured_stderr):
                with patch("app.st", mock_st):
                    load_runtime_secrets()

        out = captured_stdout.getvalue()
        err = captured_stderr.getvalue()
        self.assertNotIn("SUPER_SECRET_KEY_999", out)
        self.assertNotIn("SUPER_SECRET_KEY_999", err)

    def test_env_example_contains_no_real_or_sample_secret_values(self):
        env_example_path = CODEBASE_DIR / ".env.example"
        self.assertTrue(env_example_path.exists())
        content = env_example_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                val = line.split("=", 1)[1]
                self.assertEqual(val, "", "GEMINI_API_KEY value in .env.example must be empty")

    def test_requirements_contains_exactly_two_runtime_dependencies(self):
        req_path = CODEBASE_DIR / "requirements.txt"
        self.assertTrue(req_path.exists())
        content = req_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

        self.assertEqual(len(lines), 2)
        pkg_names = {line.split(">=")[0].split("==")[0].strip() for line in lines}
        self.assertEqual(pkg_names, {"streamlit", "python-dotenv"})

    def test_readme_contains_local_secrets_and_limitations_guidance(self):
        readme_path = CODEBASE_DIR / "README.md"
        self.assertTrue(readme_path.exists())
        content = readme_path.read_text(encoding="utf-8")

        self.assertIn("streamlit run codebase/app.py", content)
        self.assertIn("Secrets", content)
        self.assertIn("SQLite", content)
        self.assertIn("authentication", content.lower())


if __name__ == "__main__":
    unittest.main()
