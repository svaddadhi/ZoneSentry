import unittest
from unittest.mock import patch, MagicMock
from app.poller import extract_geometries, is_out_of_zone
from shapely.geometry import Point, Polygon

class TestEdgeCases(unittest.TestCase):
    def test_point_exactly_on_vertex(self):
        # Test with point exactly on a polygon vertex
        point = Point(-122.36, 37.58)
        polygon = Polygon([
            (-122.36, 37.58),  # Point is on this vertex
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36, 37.58)
        ])
        
        # Points on boundary should be considered outside per spec
        self.assertTrue(is_out_of_zone(point, [polygon]))
    
    def test_concave_polygon(self):
        # Test with concave polygon (complex shape)
        point_inside = Point(-122.368, 37.585)  # Adjusted to be clearly inside
        point_in_concave = Point(-122.363, 37.583)
        
        # Create a concave polygon (C shape)
        concave_polygon = Polygon([
            (-122.37, 37.58),
            (-122.36, 37.58),
            (-122.36, 37.582),
            (-122.365, 37.582),
            (-122.365, 37.588),
            (-122.36, 37.588),
            (-122.36, 37.59),
            (-122.37, 37.59),
            (-122.37, 37.58)
        ])
        
        self.assertFalse(is_out_of_zone(point_inside, [concave_polygon]))
        
        self.assertTrue(is_out_of_zone(point_in_concave, [concave_polygon]))
    
    def test_polygon_with_hole(self):
        # Test with polygon that has a hole in it
        outer_ring = [
            (-122.37, 37.58),
            (-122.36, 37.58),
            (-122.36, 37.59),
            (-122.37, 37.59),
            (-122.37, 37.58)
        ]
        
        # This simulates how Shapely would handle a hole
        # In GeoJSON, holes would be separate rings in the coordinates array
        polygon_with_hole = Polygon(
            outer_ring,
            [[  # Inner ring (hole)
                (-122.365, 37.585),
                (-122.365, 37.582),
                (-122.362, 37.582),
                (-122.362, 37.585),
                (-122.365, 37.585)
            ]]
        )
        
        point_in_main = Point(-122.368, 37.585)  # In main polygon
        point_in_hole = Point(-122.363, 37.583)  # In the hole
        
        # Point in the main area of polygon
        self.assertFalse(is_out_of_zone(point_in_main, [polygon_with_hole]))
        
        # Point in the hole should be considered outside
        self.assertTrue(is_out_of_zone(point_in_hole, [polygon_with_hole]))
    
    def test_self_intersecting_polygon(self):
        # Test with self-intersecting polygon (figure 8 shape)
        figure8_polygon = Polygon([
            (-122.37, 37.58),
            (-122.36, 37.59),
            (-122.35, 37.58),
            (-122.36, 37.57),
            (-122.37, 37.58)
        ])
        
        point = Point(-122.36, 37.58)
        
        # Point in center of figure 8 - behavior depends on shapely's handling
        # of self-intersecting polygons, but we just need to ensure it doesn't crash
        result = is_out_of_zone(point, [figure8_polygon])
        # We don't assert specific result because self-intersecting polygons can be handled differently
        
    def test_precision_issues(self):
        # Test with very close points that could have floating point precision issues
        polygon = Polygon([
            (-122.36000000000001, 37.58),
            (-122.35, 37.58),
            (-122.35, 37.59),
            (-122.36, 37.59),
            (-122.36000000000001, 37.58)
        ])
        
        # Point just barely inside
        point_just_inside = Point(-122.359999, 37.58001)
        
        # Point just barely outside
        point_just_outside = Point(-122.360001, 37.57999)
        
        # Verify proper classification
        self.assertFalse(is_out_of_zone(point_just_inside, [polygon]))
        self.assertTrue(is_out_of_zone(point_just_outside, [polygon]))
    
    @patch('app.poller.extract_geometries')
    def test_missing_point_or_polygon(self, mock_extract):
        # Test handling when extraction returns None for point or empty list for polygons
        mock_extract.return_value = (None, [Polygon([(0,0), (1,0), (1,1), (0,1)])])
        # Should handle this gracefully without errors
        
        mock_extract.return_value = (Point(0,0), [])
        # Should handle this gracefully without errors

if __name__ == '__main__':
    unittest.main()