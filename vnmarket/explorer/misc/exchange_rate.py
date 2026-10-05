import base64
import datetime
import warnings
from io import BytesIO

import pandas as pd
import requests

warnings.filterwarnings(
    "ignore", message="Workbook contains no default style, apply openpyxl's default"
)
from vnmarket.core.constants import DEFAULT_TIMEOUT  # noqa: E402
from vnmarket.core.exceptions import DataFetchError  # noqa: E402
from vnmarket.core.utils.logger import get_logger  # noqa: E402
from vnmarket.core.utils.parser import camel_to_snake  # noqa: E402

logger = get_logger(__name__)


def vcb_exchange_rate(date=""):
    """
    Get exchange rate from Vietcombank for a specific date.

    Parameters:
        date (str): Date in format YYYY-MM-DD. If left blank, the current date will be used.

    Raises:
        ValueError: If the date is not formatted YYYY-MM-DD.
        DataFetchError: If the request fails or the payload is unexpected.
    """  # noqa: W293
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError("Incorrect date format. Should be YYYY-MM-DD.") from e

    url = f"https://www.vietcombank.com.vn/api/exchangerates/exportexcel?date={date}"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as e:
        raise DataFetchError("Cannot reach Vietcombank API", provider="vcb") from e
    if response.status_code != 200:
        raise DataFetchError(
            "Vietcombank exchange rate request failed",
            provider="vcb",
            status_code=response.status_code,
        )
    try:
        excel_data = base64.b64decode(response.json()["Data"])
        df = pd.read_excel(BytesIO(excel_data), sheet_name="ExchangeRate")
    except (ValueError, KeyError, TypeError) as e:
        raise DataFetchError("Unexpected Vietcombank payload", provider="vcb") from e
    df.columns = ["CurrencyCode", "CurrencyName", "Buy Cash", "Buy Transfer", "Sell"]
    df = df.iloc[2:-4]
    df["date"] = date
    df.columns = [camel_to_snake(col) for col in df.columns]
    return df
