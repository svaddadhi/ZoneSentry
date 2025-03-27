import unittest
from shapely.geometry import Point, Polygon
from app.poller import extract_geometries, is_out_of_zone

class TestGeospatialFunctions(unittest.TestCase):
    def test_extract_point_and_polygon(self):
        # Test a standard response with point and polygon
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.3680236578, 37.5871044834]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.36, 37.58],
                            [-122.35, 37.58],
                            [-122.35, 37.59],
                            [-122.36, 37.59],
                            [-122.36, 37.58]
                        ]]
                    }
                }
            ]
        }
        
        point, polygons = extract_geometries(geojson)
        self.assertIsNotNone(point)
        self.assertEqual(len(polygons), 1)
        self.assertEqual(point.x, -122.3680236578)
        self.assertEqual(point.y, 37.5871044834)
    
    def test_extract_with_multiple_polygons(self):
        # Test response with point and multiple polygons
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.28, 37.51]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.30, 37.54],
                            [-122.31, 37.53],
                            [-122.29, 37.53],
                            [-122.30, 37.54]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.28, 37.52],
                            [-122.29, 37.51],
                            [-122.28, 37.51],
                            [-122.28, 37.52]
                        ]]
                    }
                }
            ]
        }
        
        point, polygons = extract_geometries(geojson)
        self.assertIsNotNone(point)
        self.assertEqual(len(polygons), 2)
    
    def test_extract_with_missing_point(self):
        # Test response with missing point
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.36, 37.58],
                            [-122.35, 37.58],
                            [-122.35, 37.59],
                            [-122.36, 37.59],
                            [-122.36, 37.58]
                        ]]
                    }
                }
            ]
        }
        
        point, polygons = extract_geometries(geojson)
        self.assertIsNone(point)
        self.assertEqual(len(polygons), 1)
    
    def test_extract_with_missing_polygon(self):
        # Test response with missing polygon
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.36, 37.58]
                    }
                }
            ]
        }
        
        point, polygons = extract_geometries(geojson)
        self.assertIsNotNone(point)
        self.assertEqual(len(polygons), 0)
    
    def test_empty_geojson(self):
        # Test with empty GeoJSON
        geojson = {"type": "FeatureCollection", "features": []}
        point, polygons = extract_geometries(geojson)
        self.assertIsNone(point)
        self.assertEqual(len(polygons), 0)
    
    def test_malformed_geojson(self):
        # Test with malformed GeoJSON
        geojson = {"type": "FeatureCollection"}  # Missing features
        point, polygons = extract_geometries(geojson)
        self.assertIsNone(point)
        self.assertEqual(len(polygons), 0)
    
    def test_point_inside_polygon(self):
        # Test point inside polygon
        point = Point(-122.355, 37.585)
        polygon = Polygon([
            (-122.36, 37.58),
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36, 37.58)
        ])
        
        self.assertFalse(is_out_of_zone(point, [polygon]))
    
    def test_point_outside_polygon(self):
        # Test point outside polygon
        point = Point(-122.37, 37.59)
        polygon = Polygon([
            (-122.36, 37.58),
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36, 37.58)
        ])
        
        self.assertTrue(is_out_of_zone(point, [polygon]))
    
    def test_point_on_polygon_boundary(self):
        # Test point on polygon boundary
        point = Point(-122.36, 37.585)
        polygon = Polygon([
            (-122.36, 37.58),
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36, 37.58)
        ])
        
        # Since we're using contains(), points on boundary are considered outside
        self.assertTrue(is_out_of_zone(point, [polygon]))
    
    def test_point_inside_one_of_multiple_polygons(self):
        # Test point inside one of multiple polygons
        point = Point(-122.285, 37.515)
        polygon1 = Polygon([
            (-122.30, 37.54),
            (-122.31, 37.53),
            (-122.29, 37.53),
            (-122.30, 37.54)
        ])
        polygon2 = Polygon([
            (-122.29, 37.52),
            (-122.28, 37.51),
            (-122.27, 37.52),
            (-122.29, 37.52)
        ])
        
        self.assertFalse(is_out_of_zone(point, [polygon1, polygon2]))
    
    def test_point_outside_all_polygons(self):
        # Test point outside all polygons
        point = Point(-122.37, 37.59)
        polygon1 = Polygon([
            (-122.36, 37.58),
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36, 37.58)
        ])
        polygon2 = Polygon([
            (-122.34, 37.57),
            (-122.33, 37.57),
            (-122.33, 37.58),
            (-122.34, 37.58),
            (-122.34, 37.57)
        ])
        
        self.assertTrue(is_out_of_zone(point, [polygon1, polygon2]))
    
    def test_no_polygons(self):
        # Test with no polygons
        point = Point(-122.36, 37.58)
        self.assertTrue(is_out_of_zone(point, []))

if __name__ == '__main__':
    unittest.main()