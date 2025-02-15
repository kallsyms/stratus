import datetime
import numpy
import pymongo
import pytest
import lzma
import array
import pytz

from wx_explore.common.storage.mongo import MongoBackend
from wx_explore.common.models import Projection, SourceField, Metric

def test_compression_roundtrip():
    # Create test data
    test_data = numpy.array([1.5, 2.5, 3.5, 4.5], dtype=numpy.float32)
    
    # Test compression and decompression
    compressed = lzma.compress(test_data.tobytes())
    decompressed = array.array("f", lzma.decompress(compressed)).tolist()
    
    # Verify data integrity
    numpy.testing.assert_array_almost_equal(test_data, decompressed)

def test_mongo_backend_compression(mocker):
    # Mock MongoDB client and collection
    mock_collection = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_client.__getitem__.return_value.__getitem__.return_value = mock_collection
    mocker.patch('pymongo.MongoClient', return_value=mock_client)
    
    # Create test instance
    backend = MongoBackend('mongodb://test', 'test_db', 'test_collection')
    
    # Create test data
    proj = Projection(id=1, n_x=4, n_y=4)
    metric = Metric(id=1)
    source_field = SourceField(id=1, metric=metric)
    valid_time = datetime.datetime.now(pytz.UTC)
    run_time = datetime.datetime.now(pytz.UTC)
    test_data = numpy.array([[1.5, 2.5, 3.5, 4.5]], dtype=numpy.float32)
    
    # Test put_fields
    fields = {(source_field.id, valid_time, run_time): [test_data]}
    backend.put_fields(proj, fields)
    
    # Verify compression was used in insert
    insert_calls = mock_collection.insert_many.call_args_list
    assert len(insert_calls) == 1
    inserted_docs = insert_calls[0][0][0]
    
    # Get the compressed field data
    field_key = f"sf{source_field.id}"
    compressed_data = list(inserted_docs.values())[0][field_key]
    
    # Verify we can decompress and get original data
    decompressed = array.array("f", lzma.decompress(compressed_data)).tolist()
    numpy.testing.assert_array_almost_equal(test_data[0], decompressed)

def test_mongo_backend_get_fields(mocker):
    # Mock MongoDB client and collection
    mock_collection = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_client.__getitem__.return_value.__getitem__.return_value = mock_collection
    mocker.patch('pymongo.MongoClient', return_value=mock_client)
    
    # Create test instance
    backend = MongoBackend('mongodb://test', 'test_db', 'test_collection')
    
    # Create test data
    test_data = numpy.array([1.5, 2.5, 3.5, 4.5], dtype=numpy.float32)
    compressed = lzma.compress(test_data.tobytes())
    
    # Mock find results
    valid_time = datetime.datetime.now(pytz.UTC)
    run_time = datetime.datetime.now(pytz.UTC)
    mock_collection.find.return_value = [{
        'valid_time': valid_time,
        'run_time': run_time,
        'sf1': compressed
    }]
    
    # Test get_fields
    metric = Metric(id=1)
    source_field = SourceField(id=1, metric=metric)
    result = backend.get_fields(
        proj_id=1,
        loc=(1.5, 1.0),
        valid_source_fields=[source_field],
        start=valid_time - datetime.timedelta(hours=1),
        end=valid_time + datetime.timedelta(hours=1)
    )
    
    # Verify results
    assert len(result) == 1
    assert result[0].values[0] == test_data[1]  # Should get second value based on loc
    assert result[0].metric_id == metric.id
    assert result[0].source_field_id == source_field.id