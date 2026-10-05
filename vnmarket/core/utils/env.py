import os
import platform
import sys
from pathlib import Path


def get_vnmarket_directory() -> Path:
    """
    Determine .vnmarket directory based on environment.

    Returns:
        Path: Path to .vnmarket directory
    """
    return Path.home() / ".vnmarket"


def is_colab() -> bool:
    """Check if running on Google Colab"""
    return get_hosting_service() == "Google Colab"


def setup_colab_drive(auto_mount: bool = True) -> bool:
    """
    Setup Google Drive for Colab environment.

    Args:
        auto_mount: Auto-mount Drive if not already mounted

    Returns:
        bool: True if setup succeeded
    """
    if not is_colab():
        return False

    drive_path = Path("/content/drive/MyDrive/.vnmarket")

    if not drive_path.exists() and auto_mount:
        try:
            from google.colab import drive

            print("\n📋 Connecting Google Drive to save vnmarket config.\n")
            drive.mount("/content/drive")
        except Exception as e:
            print(f"Cannot mount Drive: {e}")
            return False

    drive_path.mkdir(parents=True, exist_ok=True)

    if str(drive_path) not in sys.path:
        sys.path.insert(0, str(drive_path))

    return True


def get_colab_install_command() -> str:
    """Get install command for vnmarket on Google Drive"""
    if not is_colab():
        return ""

    drive_path = "/content/drive/MyDrive/.vnmarket"
    return f"!pip install --target={drive_path} vnmarket"


def show_colab_instructions() -> None:
    """Display usage instructions for vnmarket with Google Drive"""
    if not is_colab():
        return

    drive_path = "/content/drive/MyDrive/.vnmarket"
    print("\n" + "=" * 70)
    print("🚀 VNMARKET ON GOOGLE COLAB")
    print("=" * 70)
    print(f"\n  !pip install --target={drive_path} vnmarket\n")
    print("🔄 In subsequent sessions:")
    print("  from vnmarket.core.utils.env import setup_colab_drive")
    print("  setup_colab_drive()")
    print("  import vnmarket")
    print("\n" + "=" * 70 + "\n")


def get_vnmarket_path() -> Path:
    """
    Get .vnmarket directory path.
    Auto-handles Colab Drive if available.
    """
    if is_colab():
        drive_path = Path("/content/drive/MyDrive/.vnmarket")
        if drive_path.exists():
            return drive_path

    return Path.home() / ".vnmarket"


def get_platform():
    """Get the name of the running operating system"""
    return platform.system()


def get_hosting_service():
    """Identify cloud service or development environment currently running"""
    hosting_service = "Local or Unknown"
    try:
        if "google.colab" in sys.modules:
            hosting_service = "Google Colab"
        elif "CODESPACE_NAME" in os.environ:
            hosting_service = "Github Codespace"
        elif "REPLIT_USER" in os.environ:
            hosting_service = "Replit"
        elif "KAGGLE_CONTAINER_NAME" in os.environ:
            hosting_service = "Kaggle"
        elif "SPACE_HOST" in os.environ and ".hf.space" in os.environ["SPACE_HOST"]:
            hosting_service = "Hugging Face Spaces"
    except Exception:
        pass
    return hosting_service


def get_package_path(package="vnmarket"):
    """Get the path of any Python package"""
    from importlib.util import find_spec

    spec = find_spec(package)
    if spec and spec.origin:
        package_path = spec.origin
    elif spec and spec.submodule_search_locations:
        package_path = spec.submodule_search_locations[0]
    else:
        package_path = None
    return package_path


def get_username():
    """Get the current username of the system."""
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER", os.environ.get("USERNAME", None))


def get_cwd():
    """Return current working directory"""
    try:
        return os.getcwd()
    except OSError:
        return None


def get_path_delimiter():
    """Detect the running OS and return the appropriate file path delimiter."""
    return "\\" if os.name == "nt" else "/"


def detect_venv() -> dict:
    """
    Detect the current virtual environment and return its info.

    Returns:
        dict: Contains 'path' (venv path or None), 'is_active' (bool),
              'type' (str: 'venv', 'conda', 'system'), 'python_exe' (str)
    """
    venv_path = None
    is_active = False
    venv_type = "system"
    python_exe = sys.executable

    if "VIRTUAL_ENV" in os.environ:
        venv_path = os.environ["VIRTUAL_ENV"]
        is_active = True
        if "conda" in venv_path.lower():
            venv_type = "conda"
        else:
            venv_type = "venv"
        if os.name == "nt":
            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_exe = os.path.join(venv_path, "bin", "python")
    elif hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        venv_path = sys.prefix
        is_active = True
        venv_type = "venv"
        python_exe = sys.executable
    elif "CONDA_PREFIX" in os.environ:
        venv_path = os.environ["CONDA_PREFIX"]
        is_active = True
        venv_type = "conda"
        if os.name == "nt":
            python_exe = os.path.join(venv_path, "python.exe")
        else:
            python_exe = os.path.join(venv_path, "bin", "python")
    else:
        python_exe = sys.executable

    return {
        "path": venv_path,
        "is_active": is_active,
        "type": venv_type,
        "python_exe": python_exe,
    }


def get_python_executable() -> str:
    """Get the path to the Python executable for current environment."""
    venv_info = detect_venv()
    return venv_info["python_exe"]


def get_python_version_string() -> str:
    """Get Python version string for current environment."""
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def is_venv_active() -> bool:
    """Check if running in an active virtual environment."""
    return detect_venv().get("is_active", False)


def get_venv_type() -> str:
    """Get type of current virtual environment."""
    return detect_venv().get("type", "system")
