from abc import abstractmethod
from typing import Optional
import datetime
import logging

from wx_explore.common.models import Source
from wx_explore.analysis.transformations import cartesian_to_polar
from wx_explore.common import metrics
from wx_explore.common.models import (
    Source,
    SourceField,
)
from wx_explore.ingest.common import get_or_create_projection
from wx_explore.ingest.grib import get_end_valid_time
from wx_explore.web.core import db

logger = logging.getLogger(__name__)


class IngestSource(object):
    SOURCE_NAME = None

    @classmethod
    def get_db_source(cls):
        return Source.query.filter(Source.short_name == cls.SOURCE_NAME).first()

    @classmethod
    def generate_derived(cls, grib):
        logger.info("Deriving wind")

        speed_sf = SourceField.query.filter(
            SourceField.source.has(Source.short_name == cls.SOURCE_NAME),
            SourceField.metric == metrics.wind_speed,
        ).first()
        direction_sf = SourceField.query.filter(
            SourceField.source.has(Source.short_name == cls.SOURCE_NAME),
            SourceField.metric == metrics.wind_direction,
        ).first()

        if speed_sf is None or direction_sf is None:
            raise Exception("Unable to load wind speed and/or direction source fields")

        # XXX: switch to using group_by_time from analysis
        uv_pairs = zip(
            sorted(grib.select(name='10 metre U wind component', stepType='instant'), key=lambda m: (m.validDate, m.analDate)),
            sorted(grib.select(name='10 metre V wind component', stepType='instant'), key=lambda m: (m.validDate, m.analDate)),
        )

        logging.debug("Got uv_pairs")

        projection = None
        to_insert = {}

        for u, v in uv_pairs:
            speed, direction = cartesian_to_polar(u.values, v.values)
            logging.debug("Derived speed, direction")

            msg = u  # or v - this only matters for projection, valid/analysis dates, etc.

            valid_date = get_end_valid_time(msg)

            to_insert.update({
                (speed_sf.id, valid_date, msg.analDate): [speed],
                (direction_sf.id, valid_date, msg.analDate): [direction],
            })

            if projection is None:
                projection = get_or_create_projection(msg)

                if speed_sf.projection is None:
                    speed_sf.projection_id = projection.id
                elif speed_sf.projection != projection:
                    logger.error("Projection change in speed field")

                if direction_sf.projection is None:
                    direction_sf.projection_id = projection.id
                elif direction_sf.projection != projection:
                    logger.error("Projection change in direction field")

                db.session.commit()

        if projection is not None:
            return {
                projection: to_insert,
            }

        else:
            logger.warning("No U/V pairs ingested")
            return {}


    @staticmethod
    @abstractmethod
    def queue(
            time_min: int,
            time_max: int,
            run_time: Optional[datetime.datetime] = None,
            acquire_time: Optional[datetime.datetime] = None
    ):
        raise NotImplementedError
