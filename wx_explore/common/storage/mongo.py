from typing import Dict, Tuple, List, Any

import array
import concurrent.futures
import datetime
import logging
import numpy
import pymongo
import pytz
import zlib
import lzma

from . import DataProvider
from wx_explore.common import tracing
from wx_explore.common.models import (
    Projection,
    SourceField,
    DataPointSet,
)


class MongoBackend(DataProvider):
    logger: logging.Logger
    account_name: str
    account_key: str
    table_name: str
    n_x_per_row: int = 128

    def __init__(self, uri: str, database: str, collection: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.collection = pymongo.MongoClient(uri)[database][collection]
        self.collection.create_index([
            ('proj_id', pymongo.ASCENDING),
            ('valid_time', pymongo.ASCENDING),
            ('y', pymongo.ASCENDING),
        ])

    def get_fields(
            self,
            proj_id: int,
            loc: Tuple[float, float],
            valid_source_fields: List[SourceField],
            start: datetime.datetime,
            end: datetime.datetime
    ) -> List[DataPointSet]:
        x, y = loc

        nearest_row_x = ((x // self.n_x_per_row) * self.n_x_per_row)
        rel_x = x - nearest_row_x

        with tracing.start_span('get_fields lookup'):
            results = self.collection.find({
                'proj_id': proj_id,
                'y': y,
                'x_shard': nearest_row_x,
                'valid_time': {
                    '$gte': start,
                    '$lt': end,
                },
            })

        data_points = []

        for item in results:
            for sf in valid_source_fields:
                key = f"sf{sf.id}"
                if key not in item or item[key] is None:
                    continue

                compressed_data = item[key]
                # Check if data is in new format (prefixed with compression type)
                if isinstance(compressed_data, dict) and 'format' in compressed_data:
                    if compressed_data['format'] == 'lzma':
                        raw = lzma.decompress(compressed_data['data'])
                    else:  # fallback to zlib
                        raw = zlib.decompress(compressed_data['data'])
                else:  # legacy format - assume zlib
                    raw = zlib.decompress(compressed_data)
                val = array.array("f", raw).tolist()[rel_x]

                data_point = DataPointSet(
                    values=[val],
                    metric_id=sf.metric.id,
                    valid_time=item['valid_time'].replace(tzinfo=pytz.UTC),
                    source_field_id=sf.id,
                    run_time=item['run_time'].replace(tzinfo=pytz.UTC),
                )

                data_points.append(data_point)

        return data_points

    def put_fields(
            self,
            proj: Projection,
            fields: Dict[Tuple[int, datetime.datetime, datetime.datetime], List[numpy.array]]
    ):
        # fields is map of (field_id, valid_time, run_time) -> [msg, ...]
        with concurrent.futures.ThreadPoolExecutor(1) as ex:
            ex.map(lambda y: self._put_fields_worker(proj, fields, y), range(proj.n_y))

    def _put_fields_worker(
            self,
            proj: Projection,
            fields: Dict[Tuple[int, datetime.datetime, datetime.datetime], List[numpy.array]],
            y: int
    ):
        rows: Dict[Tuple[datetime.datetime, datetime.datetime, int], Dict[str, Any]] = {}

        with tracing.start_span('put_fields transformations') as span:
            span.set_attribute("num_fields", len(fields))

            for (field_id, valid_time, run_time), msgs in fields.items():
                for x in range(0, proj.n_x, self.n_x_per_row):
                    row_key = (valid_time, run_time, x)

                    if row_key not in rows:
                        rows[row_key] = {
                            'proj_id': proj.id,
                            'valid_time': valid_time,
                            'run_time': run_time,
                            'y': y,
                            'x_shard': x,
                        }

                    for msg in msgs:
                        # XXX: this only keeps last msg per field breaking ensembles
                        compressed_data = lzma.compress(msg[y][x:x+self.n_x_per_row].astype(numpy.float32).tobytes())
                        rows[row_key][f"sf{field_id}"] = {
                            'format': 'lzma',
                            'data': compressed_data
                        }

        with tracing.start_span('put_fields saving') as span:
            self.collection.insert_many(rows.values())

    def clean(self, oldest_time: datetime.datetime):
        for proj in Projection.query.all():
            self.collection.remove({
                'proj_id': proj.id,
                'valid_time': {
                    '$lt': oldest_time,
                },
            })

    def merge(self):
        pass

    def migrate_to_lzma(self, batch_size: int = 1000):
        """
        Migrate existing zlib compressed data to lzma format.
        This method processes documents in batches to avoid memory issues.
        
        Args:
            batch_size: Number of documents to process in each batch
        """
        self.logger.info("Starting migration from zlib to lzma compression")
        
        with tracing.start_span('migrate_to_lzma'):
            cursor = self.collection.find({})
            total_processed = 0
            
            while True:
                batch = list(cursor.limit(batch_size))
                if not batch:
                    break
                    
                updates = []
                for doc in batch:
                    doc_updates = {}
                    for key, value in doc.items():
                        if key.startswith('sf') and value is not None:
                            # Skip if already in new format
                            if isinstance(value, dict) and 'format' in value:
                                continue
                                
                            try:
                                # Decompress with zlib and recompress with lzma
                                raw_data = zlib.decompress(value)
                                compressed_data = lzma.compress(raw_data)
                                doc_updates[key] = {
                                    'format': 'lzma',
                                    'data': compressed_data
                                }
                            except Exception as e:
                                self.logger.error(f"Failed to migrate field {key} in document {doc['_id']}: {e}")
                                continue
                    
                    if doc_updates:
                        updates.append(pymongo.UpdateOne(
                            {'_id': doc['_id']},
                            {'$set': doc_updates}
                        ))
                
                if updates:
                    try:
                        self.collection.bulk_write(updates)
                        total_processed += len(updates)
                        self.logger.info(f"Migrated {total_processed} documents to lzma compression")
                    except Exception as e:
                        self.logger.error(f"Failed to update batch: {e}")
                
            self.logger.info(f"Migration complete. Total documents processed: {total_processed}")