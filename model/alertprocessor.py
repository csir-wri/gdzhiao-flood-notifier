"""The flood notifier model."""

import csv
import logging
from itertools import chain
from pathlib import Path
from sys import stderr
from typing import Iterable, Union

import geopandas as gpd
import rasterio
from numpy import amax
from rasterio.mask import mask

from model.recipient import Recipient


class AlertProcessor:
    """The flood notifier model"""

    def __init__(self) -> None:
        """Creates a new instance of the flood notifier model"""
        logging.basicConfig(stream=stderr, level=logging.INFO)

        self.user_db = None
        self.recipients = []
        self.rois = {}

    def get_alerts(self, model_output: Union[str, Path]):
        """Gets the alerts to be sent for the given model output.

        Args:
            model_output (Union[str, Path]): Path to the model output file

        Yields:
            dict: a dictionary of the form {"email": str,
                                            "roi": str,
                                            "towns": [(str, float),...]}

        """  # mask each of the ROIs and compute the alerts based on that

        with rasterio.open(model_output, "r+") as raster:
            for roi_name, value in self.rois.items():
                # discard the out_transform result from the mask method
                roi_mask, _ = mask(
                    raster, (value["geometry"],), all_touched=True, nodata=0, crop=True
                )

                roi_max_alert = amax(roi_mask)
                alerts = []

                if roi_max_alert > 0:
                    alerts.append((roi_name, "", roi_max_alert))
                    # process each affected town
                    for town_name, town_geom in value["towns_10k"].items():
                        town_mask, _ = mask(
                            raster, (town_geom,), all_touched=True, nodata=0, crop=True
                        )
                        town_max_alert = amax(town_mask)
                        if town_max_alert > 0:
                            alerts.append((roi_name, town_name, town_max_alert))

                # yield the alerts
                for emails in (r.emails for r in self.recipients if roi_name.lower() in r.rois):
                    for email in emails:
                        yield {"email": email, "roi": roi_name, "towns": alerts}

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

        user_db = Path(db_path)
        if user_db.suffix == ".csv":
            self.recipients.extend(_read_from_csv(db_path))

    def load_rois(self, rois: Iterable[Union[str, Path]]):
        """Loads the regions of interest geometric data.

        Args:
            rois (Iterable[Union[str, Path]]): Iterable of FilePaths containing
            the ROI geometric data.
        """

        for path in (Path(p) for p in rois):
            if path.exists() and path.is_file():
                self.rois.update(
                    (name, {"geometry": geom, "towns": {}, "towns_10k": {}})
                    for (name, geom) in AlertProcessor._load_geometries(path)
                )

    def load_towns(self, shp_files: Iterable[Union[str, Path]]):
        """Loads the towns and communities.

        Args:
            shp_files (Iterable[Union[str, Path]]): Iterable of file paths to the
            POINT shape files of towns and communities.
        """

        assert any(self.rois), "There are no ROIs loaded."

        for name, geom in chain.from_iterable(
            AlertProcessor._load_geometries(shp_file) for shp_file in shp_files
        ):
            for val in self.rois.values():
                if val["geometry"].contains(geom):
                    val["towns"][name] = geom
                    val["towns_10k"][name] = geom.buffer(10000)  # 10km buffer
                    break
            else:
                pt = geom.representative_point()
                logging.info(
                    "No ROI was found for the town '%s' located at X:%s Y:%s",
                    f"{name:<25}",
                    pt.x,
                    pt.y,
                )

    @staticmethod
    def _load_geometries(path: Union[str, Path]):
        """Loads the geometric data in the resource with the specified path.

        Args:
            path (Union[str, Path]): Path to the resource containing geometric data.

        Yields:
            tuple[str, geometry]: A tuple containing the name and geometry loaded from the data.
        """
        gdf = gpd.read_file(path)

        # normalize column names
        gdf.columns = [col.lower() for col in gdf.columns]

        # ensure the name and geometry columns are present
        assert "name" in gdf.columns, (
            f"There is no <Name> field in the attribute table.\nFile name: {path!s}"
        )
        assert "geometry" in gdf.columns, (
            f"The file does not contain any geometric data.\nFile name: {path!s}"
        )

        # yield the rows
        for name, geom in ((str(row[1]["name"]), row[1]["geometry"]) for row in gdf.iterrows()):
            yield (name, geom)
