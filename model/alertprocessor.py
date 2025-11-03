"""The flood notifier model."""

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from sys import stderr
from typing import Iterable, Optional, Sequence, Union

from model.recipient import Recipient

# cSpell: ignoreCompoundWords


@dataclass(frozen=True)
class ForecastEntry:
    date: datetime
    mean: float
    corrected: float
    thresholds: tuple[float, ...]

    @property
    def alert_level(self):
        levels = zip("GREEN YELLOW ORANGE RED".split(), self.thresholds)
        return min(
            (lvl for lvl in levels if lvl[1] >= self.corrected),
            key=lambda lvl: lvl[1],
            default=("UNKNOWN", 9999),
        )


@dataclass(frozen=True)
class AlertData:
    email: Sequence[str]
    whatsapp: Optional[str]
    locations: dict[str, list[ForecastEntry]]


class AlertProcessor:
    """The flood notifier model"""

    def __init__(self) -> None:
        """Creates a new instance of the flood notifier model"""
        logging.basicConfig(stream=stderr, level=logging.INFO)

        self.recipients: list[Recipient] = []
        self.rois = {}
        self.forecasts: dict[str, list[ForecastEntry]] = {}

    def get_current_alerts(self):
        for recipient in self.recipients:
            rois = {
                location: self.forecasts[location]
                for location in recipient.rois
                if location in self.forecasts
            }
            yield AlertData(recipient.emails, recipient.phone_numbers[0], rois)

    def load_recipients(self, db_path: Union[str, Path]):
        """Loads the recipients of the flood alerts from the specified path.

        Args:
            db_path (string): path to compatible recipient database
        """

        def _read_from_csv(csv_file: Union[str, Path]) -> Iterable[Recipient]:
            with open(csv_file) as input_file:
                reader = csv.DictReader(input_file, dialect="excel")

                # ensure all the required fields are present
                missing_keys = set(Recipient.csv_fields).difference(
                    str(f) for f in reader.fieldnames
                )
                if any(missing_keys):
                    raise Exception(
                        "One or more fields could not be found in the CSV file.\n"
                        f"Missing fields: {', '.join(missing_keys)}."
                    )

                # read each recipient
                for row in reader:
                    yield Recipient(**row)

        if Path(db_path).suffix == ".csv":
            self.recipients = list(_read_from_csv(db_path))

    def load_forecasts(self, forecast_files: Iterable[Path]):
        self.forecasts.clear()

        for file in forecast_files:
            file_lines = file.read_text().splitlines(keepends=True)
            file_lines[0] = ",".join(("date", "mean", "corrected", "th1", "th2", "th3", "th4"))
            reader = csv.DictReader(file_lines)

            forecasts = []
            for row in reader:
                # ensure blank numeric fields are zeroed before processing
                for col in (col for col in row if col not in ("date",) and row[col] == ""):
                    row[col] = "0.0"

                entry = ForecastEntry(
                    datetime.fromisoformat(row["date"]),
                    float(row["mean"]),
                    float(row["corrected"]),
                    (float(row["th1"]), float(row["th2"]), float(row["th3"]), float(row["th4"])),
                )
                forecasts.append(entry)

            self.forecasts[file.stem.lower()] = forecasts

    @staticmethod
    def compose_email_alert(locations: dict[str, list[ForecastEntry]]):
        """Composes a an alert email to be sent to the recipients in the system.

        Args:
            roi_name (str): Name of the ROI for which the message is being composed
            towns (Tuple[str, float]): List of tuples containing the names of towns and risk level.

        Returns:
            str: Content of the email to be composed.
        """

        alert_locations = ", ".join([loc.title() for loc in sorted(locations.keys())])

        message = []
        message.extend(
            (
                f" {'':=^75} ",
                "",
                f" {'GDZHIAO Flood Forecasting System Alert': ^75} ",
                "",
                f" {'Generated on': <16}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
                f" {'Locations': <16}: {alert_locations or 'NO NEW ALERTS'} ",
                "",
                f" {'':=^75} ",
                "",
            )
        )

        for idx, (location_name, forecasts) in enumerate(locations.items(), start=1):
            max_alert = max(forecasts, key=lambda f: f.corrected)
            message.append(f" {'Location': <16}: {location_name.title()}")
            message.append(
                f" {'Max Alert Level': <16}: {max_alert.alert_level[0]}"
                f" ({max_alert.corrected:.2f}) "
                f" on {max_alert.date.strftime('%d-%b-%Y')}"
            )
            message.append("")
            message.append("-" * 75)
            message.append("")
            message.append(f" {'Date': <11} | {'Discharge': >11} | {'Alert Level': <14}")
            message.append(f"-{'':-<11}-|-{'':->11}-|-{'':-<14}")
            for fc in forecasts:
                message.append(
                    f" {fc.date.strftime('%d-%b-%Y'): <11} |"
                    f" {fc.corrected: >11.2f} |"
                    f" {fc.alert_level[0]: <14}",
                )
            message.append("")

            if idx < len(locations):
                message.append("-" * 75)
                message.append("")

            message.append(f" {'':=^75} ")

        return "\n".join(message)
