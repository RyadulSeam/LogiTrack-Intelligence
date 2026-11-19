"""
Smoke test — verifies the project foundation is correctly set up.
"""
import os
import sys


def test_python_version():
    """Python version must be 3.10 or higher."""
    assert sys.version_info >= (3, 10), (
        f"Python 3.10+ required, got {sys.version}"
    )


def test_project_package_importable():
    """The logitrack package must be importable."""
    import logitrack
    assert logitrack.__version__ == "1.0.0"
    assert logitrack.__project__ == "LogiTrack Intelligence"


def test_source_datasets_exist():
    """All four original source datasets must be present."""
    source_dir = os.path.join("data", "source")
    expected_files = ["Hubs.csv", "Drivers.csv", "Vehicles.csv", "Orders.csv"]
    for filename in expected_files:
        filepath = os.path.join(source_dir, filename)
        assert os.path.exists(filepath), f"Missing source file: {filepath}"
        assert os.path.getsize(filepath) > 0, f"Empty source file: {filepath}"


def test_critical_directories_exist():
    """Key project directories must exist."""
    required_dirs = [
        "configs",
        "data/source",
        "docs",
        "scripts",
        "src/logitrack",
        "database/migrations",
        "tests",
    ]
    for d in required_dirs:
        assert os.path.isdir(d), f"Missing directory: {d}"


def test_no_secrets_in_env_example():
    """The .env.example must not contain real credentials."""
    with open(".env.example", "r") as f:
        content = f.read()
    # Should contain placeholder patterns, not real values
    assert "your-neon-project-id" in content
    assert "user:password" in content
