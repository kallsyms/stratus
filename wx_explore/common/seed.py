#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)
import pathlib

from wx_explore.common.models import (
    Source,
    SourceField,
    Location,
    Timezone,
)

from wx_explore.common import metrics
from wx_explore.common.db_utils import get_or_create
from wx_explore.web.core import app, db


def seed():
    with app.app_context():
        sources = [
            Source(
                short_name='hrrr',
                name='HRRR 2D Surface Data (Sub-Hourly)',
                src_url='http://www.nco.ncep.noaa.gov/pmb/products/hrrr/',
                last_updated=None,
                coverage_area='Continental United States (CONUS)',
                update_frequency='Hourly, with sub-hourly forecasts',
                resolution='3km grid spacing',
            ),
            Source(
                short_name='nam',
                name='North American Model',
                src_url='https://www.nco.ncep.noaa.gov/pmb/products/nam/',
                last_updated=None,
                coverage_area='North America and surrounding waters',
                update_frequency='Four times daily (00Z, 06Z, 12Z, 18Z)',
                resolution='12km grid spacing for main domain',
            ),
            Source(
                short_name='gfs',
                name='Global Forecast System',
                src_url='https://www.nco.ncep.noaa.gov/pmb/products/gfs/',
                last_updated=None,
                coverage_area='Global',
                update_frequency='Four times daily (00Z, 06Z, 12Z, 18Z)',
                resolution='0.25 degree (~25km) grid spacing',
            ),
        ]

        for i, s in enumerate(sources):
            sources[i] = get_or_create(s)


        metric_meta = {
            '2m Temperature': {
                'idx_short_name': 'TMP',
                'idx_level': '2 m above ground',
                'selectors': {
                    'name': '2 metre temperature',
                },
            },
            'Visibility': {
                'idx_short_name': 'VIS',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'vis',
                },
            },
            'Rain': {
                'idx_short_name': 'CRAIN',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'crain',
                    'stepType': 'instant',
                },
            },
            'Ice': {
                'idx_short_name': 'CICEP',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'cicep',
                    'stepType': 'instant',
                },
            },
            'Freezing Rain': {
                'idx_short_name': 'CFRZR',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'cfrzr',
                    'stepType': 'instant',
                },
            },
            'Snow': {
                'idx_short_name': 'CSNOW',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'csnow',
                    'stepType': 'instant',
                },
            },
            'Composite Reflectivity': {
                'idx_short_name': 'REFC',
                'idx_level': 'entire atmosphere',
                'selectors': {
                    'shortName': 'refc',
                },
            },
            '2m Humidity': {
                'idx_short_name': 'SPFH',
                'idx_level': '2 m above ground',
                'selectors': {
                    'name': '2 metre specific humidity',
                    'typeOfLevel': 'heightAboveGround',
                    'level': 2,
                },
            },
            'Surface Pressure': {
                'idx_short_name': 'PRES',
                'idx_level': 'surface',
                'selectors': {
                    'name': 'Surface pressure',
                },
            },
            '10m Wind U-component': {
                'idx_short_name': 'UGRD',
                'idx_level': '10 m above ground',
            },
            '10m Wind V-component': {
                'idx_short_name': 'VGRD',
                'idx_level': '10 m above ground',
            },
            # 10m speed + direction are what we show, but are not emitted by any source.
            # The above U/V components are used to calculate it.
            '10m Wind Speed': {
                'idx_short_name': 'WIND',
                'idx_level': '10 m above ground',
                'selectors': {
                    'shortName': 'wind',
                    'typeOfLevel': 'heightAboveGround',
                    'level': 10,
                },
            },
            '10m Wind Direction': {
                'idx_short_name': 'WDIR',
                'idx_level': '10 m above ground',
                'selectors': {
                    'shortName': 'wdir',
                    'typeOfLevel': 'heightAboveGround',
                    'level': 10,
                },
            },
            'Gust Speed': {
                'idx_short_name': 'GUST',
                'idx_level': 'surface',
                'selectors': {
                    'shortName': 'gust',
                },
            },
            'Cloud Cover': {
                'idx_short_name': 'TCDC',
                'idx_level': 'entire atmosphere',
                'selectors': {
                    'shortName': 'tcc',
                    'typeOfLevel': 'atmosphere',
                },
            },
        }

        for src in sources:
            for metric in metrics.ALL_METRICS:
                # Check if the metric name exists in metric_meta and use an empty dict as fallback
                meta_dict = metric_meta.get(metric.name, {})
                get_or_create(SourceField(
                    source_id=src.id,
                    metric_id=metric.id,
                    **meta_dict,
                ))

        # customization
        nam_refc = SourceField.query.filter(
            SourceField.source.has(short_name='nam'),
            SourceField.metric == metrics.composite_reflectivity,
        ).first()
        nam_refc.idx_level = 'entire atmosphere (considered as a single layer)'

        nam_cloud_cover = SourceField.query.filter(
            SourceField.source.has(short_name='nam'),
            SourceField.metric == metrics.cloud_cover,
        ).first()
        nam_cloud_cover.idx_level = 'entire atmosphere (considered as a single layer)'
        nam_cloud_cover.selectors = {'shortName': 'tcc'}

        SourceField.query.filter(
            SourceField.source.has(short_name='hrrr'),
            SourceField.metric == metrics.cloud_cover,
        ).delete()

        db.session.commit()


        ###
        # Locations
        ###
        if Location.query.count() == 0:
            import csv
            from shapely import wkt
            from shapely.geometry import Point

            locs = []

            logging.info("Loading locations: ZIP codes")
            with open(pathlib.Path(__file__).parent.parent.parent / "data/zipcodes/US.txt", encoding="utf8") as f:
                rd = csv.reader(f, delimiter='\t', quotechar='"')
                for row in rd:
                    if not row[3]:
                        continue

                    name = row[2] + ', ' + row[3] + ' (' + row[1] + ')'
                    lat = float(row[9])
                    lon = float(row[10])
                    locs.append(Location(
                        name=name,
                        location=wkt.dumps(Point(lon, lat)),
                    ))

            logging.info("Loading locations: world cities")
            with open(pathlib.Path(__file__).parent.parent.parent / "data/cities/worldcities.csv", encoding="utf8") as f:
                f.readline()  # skip header line
                rd = csv.reader(f)
                for row in rd:
                    name = row[0] + ', ' + row[7]
                    lat = float(row[2])
                    lon = float(row[3])
                    population = None
                    if row[9]:
                        population = int(float(row[9]))
                    locs.append(Location(
                        name=name,
                        location=wkt.dumps(Point(lon, lat)),
                        population=population,
                    ))

            logging.info("Creating locations")
            db.session.add_all(locs)
            db.session.commit()


        ###
        # Timezones
        ###
        if Timezone.query.count() == 0:
            import threading
            threading.Thread(target=seed_timezones).start()

def seed_timezones():
    import geoalchemy2
    import os
    import pygeoif
    import requests
    import shapefile
    import shutil
    import tempfile
    import zipfile

    # with app.app_context():
    #     logging.info("Creating timezones")
    #     os.makedirs("/tmp/stratus_tzs", exist_ok=True)
    #     with open("/tmp/stratus_tzs/timezones-with-oceans.shapefile.zip", "wb") as f:
    #         with requests.get('https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones-with-oceans.shapefile.zip', stream=True) as resp:
    #             shutil.copyfileobj(resp.raw, f)

    #     with open("/tmp/stratus_tzs/timezones-with-oceans.shapefile.zip", "rb") as f:
    #         with zipfile.ZipFile(f) as z:
    #             z.extractall("/tmp/stratus_tzs/timezones-with-oceans.shapefile.zip")

    #     shapefile = shapefile.Reader(os.path.join("/tmp/stratus_tzs", 'dist/timezones-with-oceans.shapefile'))

    #     tzs = []

    #     for sr in shapefile.iterShapeRecords():
    #         tzs.append(Timezone(
    #             name=sr.record.tzid,
    #             geom=geoalchemy2.functions.ST_Multi(pygeoif.geometry.as_shape(sr.shape).wkt),
    #         ))

    #     db.session.add_all(tzs)
    #     db.session.commit()


if __name__ == "__main__":
    seed()