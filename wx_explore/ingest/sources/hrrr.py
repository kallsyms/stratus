#!/usr/bin/env python3
from datetime import datetime, timedelta
from typing import Optional

import argparse
import logging

from wx_explore.common.log_setup import init_sentry
from wx_explore.common.utils import datetime2unix
from wx_explore.ingest.common import get_queue
from wx_explore.ingest.sources.source import IngestSource

logger = logging.getLogger(__name__)


class HRRR(IngestSource):
    SOURCE_NAME = "hrrr"

    @staticmethod
    def queue(
            time_min: int = 0,
            time_max: int = 18,
            run_time: Optional[datetime] = None,
            acquire_time: Optional[datetime] = None
    ):
        if run_time is None:
            # hrrr is run each hour
            run_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        if acquire_time is None:
            # first files are available about 45 mins after
            acquire_time = run_time
            acquire_time += timedelta(minutes=45)

        base_url = run_time.strftime("https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf{}.grib2")

        q = get_queue()
        for hr in range(time_min, time_max + 1):
            url = base_url.format(str(hr).zfill(2))
            q.put({
                "source": "hrrr",
                "valid_time": datetime2unix(run_time + timedelta(hours=hr)),
                "run_time": datetime2unix(run_time),
                "url": url,
                "idx_url": url+".idx",
            }, schedule_at=acquire_time)


if __name__ == "__main__":
    init_sentry()
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Ingest HRRR')
    parser.add_argument('--offset', type=int, default=0, help='Run offset to ingest')
    args = parser.parse_args()

    run_time = datetime.utcnow()
    run_time = run_time.replace(minute=0, second=0, microsecond=0)
    run_time -= timedelta(hours=args.offset)
    HRRR.queue(run_time=run_time)
