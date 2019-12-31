#!/usr/bin/env python3
from datetime import datetime, timedelta
import logging

from wx_explore.common.utils import datetime2unix
from wx_explore.ingest import get_queue


def queue_hrrr(time_min=0, time_max=18, run_time=None, acquire_time=None):
    if run_time is None:
        # hrrr is run each hour
        run_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    if acquire_time is None:
        # first files are available about 45 mins after
        acquire_time = run_time
        acquire_time += timedelta(minutes=45)

    base_url = run_time.strftime("https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf{}.grib2")

    urls = [base_url.format(str(x).zfill(2)) for x in range(time_min, time_max + 1)]

    q = get_queue()
    for url in urls:
        q.put({
            "source": "hrrr",
            "run_time": datetime2unix(run_time),
            "url": url,
            "idx_url": url+".idx",
        }, schedule_at=acquire_time)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    queue_hrrr()
