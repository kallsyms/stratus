import datetime
import numpy as np
import pytest
import pytz
import lzma

from wx_explore.common.models import Projection, SourceField, Metric
from wx_explore.common.storage.mongo import MongoBackend

class TestMongoStorage:
    @pytest.fixture
    def mongo_backend(self):
        # Use a test database
        backend = MongoBackend("mongodb://localhost:27017", "test_wx_explore", "test_collection")
        yield backend
        # Clean up the test collection after each test
        backend.collection.drop()
        
    @pytest.fixture
    def test_data(self):
        # Create test projection
        proj = Projection(
            id=1,
            name="test_proj",
            n_x=256,
            n_y=256,
            proj4="+proj=longlat +datum=WGS84 +no_defs",
        )
        
        # Create test metric
        metric = Metric(
            id=1,
            name="temperature",
            unit="K",
        )
        
        # Create test source field
        source_field = SourceField(
            id=1,
            name="temp_2m",
            metric=metric,
            projection=proj,
        )
        
        # Create test data array
        data = np.random.rand(256, 128).astype(np.float32)
        
        return proj, source_field, data
        
    def test_compression_switch(self, mongo_backend, test_data):
        """Test that data can be compressed with lzma and retrieved correctly"""
        proj, source_field, data = test_data
        
        # Create test timestamp
        valid_time = datetime.datetime.now(pytz.UTC)
        run_time = valid_time - datetime.timedelta(hours=1)
        
        # Store data
        fields = {
            (source_field.id, valid_time, run_time): [data]
        }
        
        # Put fields should now use lzma compression internally
        mongo_backend.put_fields(proj, fields)
        
        # Retrieve data for a specific point
        test_loc = (64.0, 64.0)  # Some point within our grid
        retrieved = mongo_backend.get_fields(
            proj.id,
            test_loc,
            [source_field],
            valid_time - datetime.timedelta(minutes=1),
            valid_time + datetime.timedelta(minutes=1)
        )
        
        assert len(retrieved) == 1
        assert retrieved[0].source_field_id == source_field.id
        assert retrieved[0].valid_time == valid_time
        assert retrieved[0].run_time == run_time
        
        # The retrieved value should match our input data at that location
        x, y = test_loc
        expected_val = data[int(y)][int(x)]
        assert abs(retrieved[0].values[0] - expected_val) < 1e-6
        
    def test_compression_ratio(self, mongo_backend, test_data):
        """Test that lzma compression provides reasonable compression ratios"""
        proj, source_field, data = test_data
        
        # Get raw data size
        raw_size = len(data.tobytes())
        
        # Get lzma compressed size
        lzma_size = len(lzma.compress(data.tobytes()))
        
        # LZMA should provide good compression for floating point data
        assert lzma_size < raw_size
        
    def test_large_array_handling(self, mongo_backend, test_data):
        """Test that large arrays are handled correctly with lzma compression"""
        proj, source_field, _ = test_data
        
        # Create a larger test array
        large_data = np.random.rand(1024, 512).astype(np.float32)
        
        valid_time = datetime.datetime.now(pytz.UTC)
        run_time = valid_time - datetime.timedelta(hours=1)
        
        fields = {
            (source_field.id, valid_time, run_time): [large_data]
        }
        
        # Should handle large arrays without issues
        mongo_backend.put_fields(proj, fields)
        
        # Test retrieval from different points in the array
        test_points = [(100.0, 100.0), (400.0, 200.0), (800.0, 400.0)]
        
        for test_loc in test_points:
            retrieved = mongo_backend.get_fields(
                proj.id,
                test_loc,
                [source_field],
                valid_time - datetime.timedelta(minutes=1),
                valid_time + datetime.timedelta(minutes=1)
            )
            
            assert len(retrieved) == 1
            x, y = test_loc
            expected_val = large_data[int(y)][int(x)]
            assert abs(retrieved[0].values[0] - expected_val) < 1e-6