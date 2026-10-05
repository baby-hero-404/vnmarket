"""
Visualization and charting utilities for data exploration.

This module provides a pandas DataFrame/Series extension for creating
various types of charts. It supports two charting backends:

1. vnmarket_chart (Professional, if available):
   - LineChart, BarChart, CandleChart, ScatterChart, BoxplotChart, HeatmapChart

2. vnmarket_ezchart (Fallback, basic charts):
    - bar: Bar charts
    - hist: Histograms
    - pie: Pie charts
    - scatter: Scatter plots
    - heatmap: Heatmaps
    - boxplot: Box plots
    - pairplot: Pair plots
    - timeseries: Time series visualization
    - treemap: Treemap charts
    - wordcloud: Word clouds
    - table: Table visualization
    - combo_chart: Combo charts with bars and lines

Example:
    >>> import pandas as pd
    >>> from vnmarket.common.viz import Chart
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> chart = Chart(df)
    >>> chart.bar()

    Or use the convenient extension:
    >>> df.viz.bar()
    >>> df.viz.scatter(x='A', y='B')
"""

from typing import Any, Optional, Union

import pandas as pd

from vnmarket.core.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import vnmarket_chart first (professional charting library)
HAS_VNMARKET_CHART = False
try:
    import vnmarket_chart  # noqa: F401
    from vnmarket_chart import (
        BarChart,
        BoxplotChart,
        CandleChart,
        HeatmapChart,
        LineChart,
        ScatterChart,
    )

    HAS_VNMARKET_CHART = True
except ImportError:
    pass  # Silently skip if not available

# Fallback to vnmarket_ezchart if vnmarket_chart not available
HAS_VNMARKET_EZCHART = False
try:
    from vnmarket_ezchart import Chart as EzChart

    HAS_VNMARKET_EZCHART = True
except ImportError:
    try:
        # Fallback for older versions of vnmarket_ezchart
        from vnmarket_ezchart.mplot import MPlot as EzChart

        HAS_VNMARKET_EZCHART = True
    except ImportError:
        pass

# Ensure at least one charting library is available
# (Removed module-level check to make charting optional; checked in Chart.__init__ instead)


class Chart:
    """
    Chart wrapper for creating various types of data visualizations.

    Supports two charting backends:
    1. vnmarket_chart (Professional, recommended) - if available
    2. vnmarket_ezchart (Fallback) - basic charts

    Available chart methods depend on the backend:

    vnmarket_chart methods:
        - line(): Line charts
        - bar(): Bar charts
        - candle(): Candlestick charts
        - scatter(): Scatter plots
        - boxplot(): Box plots
        - heatmap(): Heatmaps

    vnmarket_ezchart methods (fallback):
        - bar(), hist(), pie(), scatter(), heatmap(), boxplot(), pairplot()
        - line(), timeseries(), treemap(), wordcloud(), table()
        - combo(), combo_chart(), candle(), equity_curve(), returns_heatmap(), summary_card()

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> chart = Chart(df)
        >>> chart.bar()

        Or use the convenient extension:
        >>> df.viz.bar()
        >>> df.viz.scatter(x='A', y='B')
    """

    def __init__(
        self, data: Union[pd.DataFrame, pd.Series], backend: Optional[str] = None
    ):
        """
        Initialize Chart instance.

        Args:
            data: pandas DataFrame or Series to visualize
            backend: Charting backend to use ('vnmarket_chart', 'vnmarket_ezchart', or None for auto)

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if not isinstance(data, (pd.DataFrame, pd.Series)):
            raise ValueError(
                f"Data must be a pandas DataFrame or Series, got {type(data).__name__}"
            )

        self.data = data
        self.backend = None
        self.chart = None

        # Determine which backend to use
        if backend == "vnmarket_chart":
            if HAS_VNMARKET_CHART:
                self.backend = "vnmarket_chart"
            else:
                raise ImportError(
                    "vnmarket_chart is not installed. Use standard plotting or install charting backend."
                )

        if backend == "vnmarket_ezchart":
            if HAS_VNMARKET_EZCHART:
                self.backend = "vnmarket_ezchart"
                self.chart = EzChart()
            else:
                raise ImportError(
                    "vnmarket_ezchart is not installed. To install:\n"
                    "pip install vnmarket_ezchart"
                )

        # Auto-select backend if not specified
        if self.backend is None:
            if HAS_VNMARKET_CHART:
                self.backend = "vnmarket_chart"
            elif HAS_VNMARKET_EZCHART:
                self.backend = "vnmarket_ezchart"
                self.chart = EzChart()
            else:
                raise ImportError(
                    "No charting library available. Please install vnmarket_ezchart or matplotlib/seaborn."
                )

        # Only log errors, not debug info
        if self.backend == "vnmarket_chart" and not HAS_VNMARKET_CHART:
            logger.error("vnmarket_chart backend selected but not available")
        elif self.backend == "vnmarket_ezchart" and not HAS_VNMARKET_EZCHART:
            logger.error("vnmarket_ezchart backend selected but not available")

    def line(self, **kwargs):
        """Create line chart using vnmarket_chart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.iloc[:, 0].values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")

                chart = LineChart(x=x, y=y, **kwargs)

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating line chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "line"):
                return self.chart.line(self.data, **kwargs)
            return self.chart.timeseries(self.data, **kwargs)
        else:
            raise AttributeError(f"line chart not available in {self.backend} backend")

    def bar(self, **kwargs):
        """Create bar chart using vnmarket_chart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.iloc[:, 0].values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")

                chart = BarChart(x=x, y=y, **kwargs)

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating bar chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            return self.chart.bar(self.data, **kwargs)
        else:
            raise AttributeError(f"bar chart not available in {self.backend} backend")

    def scatter(self, x=None, y=None, **kwargs):
        """Create scatter plot using vnmarket_chart or vnmarket_ezchart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.DataFrame):
                    if x is None or y is None:
                        if len(self.data.columns) >= 2:
                            x = x or self.data.columns[0]
                            y = y or self.data.columns[1]
                        else:
                            raise ValueError(
                                "DataFrame must have at least 2 columns for scatter plot"
                            )

                    x_data = self.data[x].tolist()
                    y_data = self.data[y].tolist()
                else:
                    raise ValueError("Scatter plot requires DataFrame")

                chart = ScatterChart(x=x_data, y=y_data, **kwargs)

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating scatter chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            if isinstance(self.data, pd.DataFrame):
                if x is None or y is None:
                    if len(self.data.columns) >= 2:
                        x = x or self.data.columns[0]
                        y = y or self.data.columns[1]
                    else:
                        raise ValueError(
                            "DataFrame must have at least 2 columns for scatter plot"
                        )
                return self.chart.scatter(self.data, x, y, **kwargs)
            else:
                raise ValueError("Scatter plot requires DataFrame for vnmarket_ezchart")
        else:
            raise AttributeError(
                f"scatter chart not available in {self.backend} backend"
            )

    def candle(self, **kwargs):
        """Create candlestick chart using vnmarket_chart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.DataFrame):
                    required_cols = ["open", "high", "low", "close"]
                    if not all(col in self.data.columns for col in required_cols):
                        raise ValueError(
                            "Candlestick chart requires 'open', 'high', 'low', 'close' columns"
                        )

                    # Prepare DataFrame with required columns
                    # Add time column if it's in index
                    df = self.data.copy()
                    if isinstance(df.index, pd.DatetimeIndex):
                        df = df.reset_index()
                        if "time" not in df.columns and df.index.name != "time":
                            df = df.rename(columns={df.columns[0]: "time"})

                    # Ensure we have volume column (required by CandleChart)
                    if "volume" not in df.columns:
                        df["volume"] = [1] * len(df)  # Default volume

                    # Reorder columns to expected order: time, open, close, low, high, volume
                    expected_cols = ["time", "open", "close", "low", "high", "volume"]
                    available_cols = [col for col in expected_cols if col in df.columns]
                    df = df[available_cols]

                    chart = CandleChart(df=df, **kwargs)
                else:
                    raise ValueError(
                        "Candlestick chart requires DataFrame with OHLC data"
                    )

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating candlestick chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "candle"):
                return self.chart.candle(self.data, **kwargs)
            # vnmarket_ezchart older versions don't have candlestick, fallback to line
            if hasattr(self.chart, "line"):
                return self.chart.line(self.data, **kwargs)
            return self.chart.timeseries(self.data, **kwargs)
        else:
            raise AttributeError(
                f"candlestick chart not available in {self.backend} backend"
            )

    def heatmap(self, **kwargs):
        """Create heatmap using vnmarket_chart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.DataFrame):
                    x = self.data.columns.tolist()
                    y = self.data.index.tolist()
                    value = self.data.values.tolist()
                else:
                    raise ValueError("Heatmap requires DataFrame")

                chart = HeatmapChart(x=x, y=y, value=value, **kwargs)

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating heatmap chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            return self.chart.heatmap(self.data, **kwargs)
        else:
            raise AttributeError(
                f"heatmap chart not available in {self.backend} backend"
            )

    def boxplot(self, **kwargs):
        """Create boxplot using vnmarket_chart."""
        if self.backend == "vnmarket_chart":
            try:
                if isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")

                chart = BoxplotChart(x=x, y=y, **kwargs)

                # Auto-render by default
                try:
                    import sys

                    if "ipykernel" in sys.modules or "IPython" in sys.modules:
                        try:
                            from IPython.display import display

                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass

                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating boxplot chart: {e}")
                raise
        elif self.backend == "vnmarket_ezchart" and self.chart:
            return self.chart.boxplot(self.data, **kwargs)
        else:
            raise AttributeError(
                f"boxplot chart not available in {self.backend} backend"
            )

    # vnmarket_ezchart specific methods
    def hist(self, **kwargs):
        """Create histogram using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            return self.chart.hist(self.data, **kwargs)
        elif self.backend == "vnmarket_chart":
            # vnmarket_chart doesn't have hist, fallback to bar
            return self.bar(**kwargs)
        else:
            raise AttributeError(
                f"histogram chart not available in {self.backend} backend"
            )

    def pie(self, labels=None, **kwargs):
        """Create pie chart using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            # Handle labels for pie chart
            if labels is None:
                if isinstance(self.data, pd.DataFrame):
                    if len(self.data.columns) >= 2:
                        labels = self.data.iloc[:, 0].tolist()
                        data = self.data.iloc[:, 1]
                    else:
                        labels = self.data.index.tolist()
                        data = self.data.iloc[:, 0]
                elif isinstance(self.data, pd.Series):
                    labels = self.data.index.tolist()
                    data = self.data
            else:
                data = self.data

            return self.chart.pie(data, labels, **kwargs)
        else:
            raise AttributeError(f"pie chart not available in {self.backend} backend")

    def timeseries(self, **kwargs):
        """Create time series chart using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "line"):
                return self.chart.line(self.data, **kwargs)
            return self.chart.timeseries(self.data, **kwargs)
        elif self.backend == "vnmarket_chart":
            # Use line chart for vnmarket_chart
            return self.line(**kwargs)
        else:
            raise AttributeError(
                f"time series chart not available in {self.backend} backend"
            )

    def treemap(self, values=None, labels=None, **kwargs):
        """Create treemap using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if values is None and labels is None:
                if isinstance(self.data, pd.DataFrame):
                    if len(self.data.columns) >= 2:
                        values = self.data.iloc[:, 0].tolist()
                        labels = self.data.iloc[:, 1].tolist()
                    else:
                        values = self.data.iloc[:, 0].tolist()
                        labels = self.data.index.tolist()
                elif isinstance(self.data, pd.Series):
                    values = self.data.values.tolist()
                    labels = self.data.index.tolist()

            return self.chart.treemap(values, labels, **kwargs)
        else:
            raise AttributeError(
                f"treemap chart not available in {self.backend} backend"
            )

    def wordcloud(self, text=None, **kwargs):
        """Create word cloud using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if text is None:
                if isinstance(self.data, pd.DataFrame):
                    # Convert DataFrame to text
                    text = " ".join(self.data.astype(str).values.flatten())
                elif isinstance(self.data, pd.Series):
                    text = " ".join(self.data.astype(str).values)
                else:
                    text = str(self.data)

            return self.chart.wordcloud(text, **kwargs)
        else:
            raise AttributeError(
                f"word cloud chart not available in {self.backend} backend"
            )

    def table(self, **kwargs):
        """Create table using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if isinstance(self.data, pd.DataFrame):
                return self.chart.table(self.data, **kwargs)
            elif isinstance(self.data, pd.Series):
                # Convert Series to DataFrame for table
                df = self.data.to_frame()
                return self.chart.table(df, **kwargs)
            else:
                raise ValueError("Table requires DataFrame or Series")
        else:
            raise AttributeError(f"table chart not available in {self.backend} backend")

    def combo_chart(self, bar_data=None, line_data=None, **kwargs):
        """Create combo chart using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if bar_data is None and line_data is None:
                if isinstance(self.data, pd.DataFrame) and len(self.data.columns) >= 2:
                    bar_data = self.data.iloc[:, 0]
                    line_data = self.data.iloc[:, 1]
                else:
                    raise ValueError(
                        "Combo chart requires DataFrame with at least 2 columns"
                    )
            elif isinstance(bar_data, str) and isinstance(self.data, pd.DataFrame):
                # If bar_data is column name, extract the Series
                bar_data = self.data[bar_data]
            if isinstance(line_data, str) and isinstance(self.data, pd.DataFrame):
                # If line_data is column name, extract the Series
                line_data = self.data[line_data]

            if hasattr(self.chart, "combo"):
                return self.chart.combo(bar_data, line_data, **kwargs)
            return self.chart.combo_chart(bar_data, line_data, **kwargs)
        else:
            raise AttributeError(f"combo chart not available in {self.backend} backend")

    def combo(self, bar_data=None, line_data=None, **kwargs):
        """Create combo chart using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if bar_data is None and line_data is None:
                if isinstance(self.data, pd.DataFrame) and len(self.data.columns) >= 2:
                    bar_data = self.data.iloc[:, 0]
                    line_data = self.data.iloc[:, 1]
                else:
                    raise ValueError(
                        "Combo chart requires DataFrame with at least 2 columns"
                    )
            elif isinstance(bar_data, str) and isinstance(self.data, pd.DataFrame):
                bar_data = self.data[bar_data]
            if isinstance(line_data, str) and isinstance(self.data, pd.DataFrame):
                line_data = self.data[line_data]

            if hasattr(self.chart, "combo"):
                return self.chart.combo(bar_data, line_data, **kwargs)
            return self.chart.combo_chart(bar_data, line_data, **kwargs)
        else:
            raise AttributeError(f"combo chart not available in {self.backend} backend")

    def equity_curve(self, benchmark=None, **kwargs):
        """Create equity curve chart using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "equity_curve"):
                return self.chart.equity_curve(self.data, benchmark=benchmark, **kwargs)
            raise AttributeError(
                "equity_curve not available in the installed version of vnmarket_ezchart"
            )
        else:
            raise AttributeError(
                f"equity_curve not available in {self.backend} backend"
            )

    def returns_heatmap(self, **kwargs):
        """Create returns heatmap using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "returns_heatmap"):
                return self.chart.returns_heatmap(self.data, **kwargs)
            raise AttributeError(
                "returns_heatmap not available in the installed version of vnmarket_ezchart"
            )
        else:
            raise AttributeError(
                f"returns_heatmap not available in {self.backend} backend"
            )

    def summary_card(self, *args, **kwargs):
        """Create summary card using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, "summary_card"):
                return self.chart.summary_card(*args, **kwargs)
            raise AttributeError(
                "summary_card not available in the installed version of vnmarket_ezchart"
            )
        else:
            raise AttributeError(
                f"summary_card not available in {self.backend} backend"
            )

    def pairplot(self, **kwargs):
        """Create pair plot using vnmarket_ezchart."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            return self.chart.pairplot(self.data, **kwargs)
        else:
            raise AttributeError(
                f"pair plot chart not available in {self.backend} backend"
            )

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown methods to vnmarket_ezchart if available."""
        if self.backend == "vnmarket_ezchart" and self.chart:
            if hasattr(self.chart, name):
                attr = getattr(self.chart, name)
                if callable(attr):

                    def method_wrapper(*args, **kwargs):
                        try:
                            if args:
                                return attr(*args, **kwargs)
                            else:
                                return attr(self.data, **kwargs)
                        except Exception as e:
                            if "not installed" not in str(e):
                                logger.error(f"Error calling {name}: {e}")
                            raise

                    return method_wrapper
                return attr

        raise AttributeError(
            f"'Chart' object has no attribute '{name}' in {self.backend} backend"
        )


def _add_viz_property(cls):
    """
    Add .viz property to pandas DataFrame and Series.

    This enables convenient chart access: df.viz.bar()

    Args:
        cls: pandas DataFrame or Series class
    """

    @property
    def viz(self):
        """
        Access visualization methods through .viz extension.

        Returns:
            Chart instance for the current DataFrame/Series

        Example:
            >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            >>> df.viz.bar()
            >>> df.viz.timeseries()
            >>> df.viz.scatter(x='A', y='B')
        """
        return Chart(self)

    cls.viz = viz


# Register .viz property with pandas classes
try:
    _add_viz_property(pd.DataFrame)
    _add_viz_property(pd.Series)
except Exception as e:
    logger.error(f"Could not register .viz extension: {e}")


def get_chart(
    data: Union[pd.DataFrame, pd.Series], backend: Optional[str] = None
) -> Chart:
    """
    Create a Chart instance from DataFrame or Series.

    Args:
        data: pandas DataFrame or Series
        backend: Charting backend ('vnmarket_chart', 'vnmarket_ezchart', or None for auto)

    Returns:
        Chart instance

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> chart = get_chart(df)
        >>> chart.bar()

        >>> # Use specific backend
        >>> chart = get_chart(df, backend='vnmarket_chart')
    """
    return Chart(data, backend=backend)


__all__ = ["Chart", "get_chart", "HAS_VNMARKET_CHART", "HAS_VNMARKET_EZCHART"]
