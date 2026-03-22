from __future__ import annotations

from io import StringIO
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd


def fetch_holidays_dataframe(
    source_url: str,
    *,
    date_column_candidates: tuple[str, ...] = ("date", "Date", "日付", "年月日"),
    timeout_seconds: float = 15.0,
    max_retries: int = 2,
    retry_wait_seconds: float = 0.5,
    encoding: str = "utf-8-sig",
) -> pd.DataFrame:
    """Fetch holiday CSV and normalize to single `date` column."""

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            with urlopen(source_url, timeout=timeout_seconds) as response:  # noqa: S310
                payload = response.read().decode(encoding)
            frame = pd.read_csv(StringIO(payload))
            return normalize_holidays_dataframe(
                frame, date_column_candidates=date_column_candidates
            )
        except (URLError, UnicodeDecodeError, ValueError) as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            time.sleep(retry_wait_seconds)

    assert last_error is not None
    raise RuntimeError(
        f"failed to fetch holidays from url={source_url}: {last_error}"
    ) from last_error


def normalize_holidays_dataframe(
    frame: pd.DataFrame,
    *,
    date_column_candidates: tuple[str, ...] = ("date", "Date", "日付", "年月日"),
) -> pd.DataFrame:
    """Normalize source frame into unique `date` rows sorted ascending."""

    lowered = {column.lower(): column for column in frame.columns}
    date_column: str | None = None

    for candidate in date_column_candidates:
        if candidate in frame.columns:
            date_column = candidate
            break
        lowered_candidate = candidate.lower()
        if lowered_candidate in lowered:
            date_column = lowered[lowered_candidate]
            break

    if date_column is None:
        raise ValueError("holiday source must include a date column")

    normalized_dates = pd.to_datetime(frame[date_column], errors="coerce").dt.normalize().dropna()
    if normalized_dates.empty:
        raise ValueError("holiday source contains no valid dates")

    normalized = pd.DataFrame({"date": normalized_dates.dt.strftime("%Y-%m-%d")})
    return normalized.drop_duplicates().sort_values("date").reset_index(drop=True)


def fetch_holidays_csv(
    source_url: str,
    out_path: str | Path,
    *,
    date_column_candidates: tuple[str, ...] = ("date", "Date", "日付", "年月日"),
    timeout_seconds: float = 15.0,
    max_retries: int = 2,
    retry_wait_seconds: float = 0.5,
    encoding: str = "utf-8-sig",
) -> Path:
    """Fetch holiday CSV and persist standardized CSV (`date` column)."""

    normalized = fetch_holidays_dataframe(
        source_url,
        date_column_candidates=date_column_candidates,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_wait_seconds=retry_wait_seconds,
        encoding=encoding,
    )

    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(target, index=False)
    return target
