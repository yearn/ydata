import calendar
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Optional

import pandas as pd


def to_timestamp(date: datetime) -> int:
    """Returned timestamp is offset-aware"""
    return int(
        (date - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds() * (10**3)
    )


def append_csv_rows(file_path: Path, rows: list[list]) -> None:
    with open(file_path, "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)


def get_csv_row(file_path: Path, line: int) -> Optional[list[str]]:
    def with_last(itr: Iterator):
        old = next(itr)
        for new in itr:
            yield False, old
            old = new
        yield True, old

    with open(file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for line_num, (is_last, row) in enumerate(with_last(reader)):
            if line_num == line or (is_last and line == -1):
                return row
    return None


def add_months(sourcedate: datetime, months: int) -> datetime:
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return sourcedate.replace(year=year, month=month, day=day, tzinfo=timezone.utc)


def update_csv(
    output_file_path: Path, cbs: list[Callable[[int, list[str]], list]]
) -> None:
    output_path = Path(output_file_path)
    output_path_ext = output_path.suffix
    directory = output_path.parent.resolve()
    temp_path = directory / f"temp{output_path_ext}"

    with open(output_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        with open(temp_path, "w") as csv_file:
            writer = csv.writer(csv_file)

            for line_num, row in enumerate(reader):
                for cb in cbs:
                    row = cb(line_num, row)
                writer.writerow(row)
    output_path.unlink()
    temp_path.rename(output_path)


def get_start_and_end_of_month(
    start_datetime: datetime, end_datetime: datetime
) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    start_rng = pd.date_range(start_datetime, end_datetime, freq="MS", tz=timezone.utc)
    end_rng = pd.date_range(start_datetime, end_datetime, freq="M", tz=timezone.utc)

    if not all([len(start_rng), len(end_rng)]):
        return []

    start_date = f"{start_rng[0].month}{start_rng[0].year}"
    end_date = f"{end_rng[0].month}{end_rng[0].year}"
    slice_end = start_date != end_date

    start_date = f"{start_rng[-1].month}{start_rng[-1].year}"
    end_date = f"{end_rng[-1].month}{end_rng[-1].year}"
    slice_start = start_date != end_date

    end_rng = end_rng[1:] if slice_end else end_rng
    start_rng = start_rng[:-1] if slice_start else start_rng

    if not all([len(start_rng), len(end_rng)]):
        return []

    return [rng for rng in zip(start_rng, end_rng)]
