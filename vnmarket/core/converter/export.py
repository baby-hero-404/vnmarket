import json
from typing import Dict

from vnmarket.core.utils.logger import get_logger

logger = get_logger(__name__)


def save_json(data: Dict, path: str = "data.json"):
    """
    Save the data as JSON.
    """
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)  # Indent for readability
        logger.info(f"Information saved to JSON file: {path}")
    except Exception as e:
        logger.error(f"Error saving data to JSON: {e}")
