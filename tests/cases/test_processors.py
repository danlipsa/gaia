#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import os
import json
import unittest
from zipfile import ZipFile
import gaia
import gaia.geo as geo
from gaia.geo.geo_inputs import RasterFileIO, VectorFileIO, FeatureIO

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
testfile_path = os.path.join(base_dir, '../data')


class TestGaiaProcessors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_file = os.path.join(base_dir, '../../gaia/conf/gaia.cfg')
        gaia.get_config(config_file)

    def test_zonalstats(self):
        vector_io = FeatureIO(features=[
            {"type": "Feature",
             "geometry": {
                 "type": "Polygon",
                 "coordinates": [
                     [[100.0, 0.0], [120.0, 0.0], [120.0, 30.0],
                      [100.0, 30.0], [100.0, 0.0]]
                 ]
             },
             "properties": {
                 "prop0": "value1",
                 "prop1": {"this": "that"}
             }
             },
            {"type": "Feature",
             "geometry": {
                 "type": "Polygon",
                 "coordinates": [
                     [[-100.0, 0.0], [-120.0, 0.0], [-120.0, -30.0],
                      [100.0, -30.0], [100.0, 0.0]]
                 ]
             },
             "properties": {
                 "prop0": "value0",
                 "prop1": {"this": "other thing"}
             }
             }])
        raster_io = RasterFileIO(name='temp', uri=os.path.join(
            testfile_path, 'globalairtemp.tif'))
        process = geo.ZonalStatsProcess(inputs=[raster_io, vector_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'zonalstats_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            pass
            if process:
                process.purge()

    def test_within(self):
        """
        Test WithinProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        process = geo.WithinProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            self.assertEquals(len(process.output.data), 19)
        finally:
            if process:
                process.purge()

    def test_intersect(self):
        """
        Test IntersectsProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = geo.IntersectsProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'intersects_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_cross(self):
        """
        Test IntersectsProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = geo.CrossesProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'crosses_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_touch(self):
        """
        Test IntersectsProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = geo.TouchesProcess(
            inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'touches_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_union(self):
        """
        Test UnionProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'),
            filters=[('NNAME', 'contains', '^A')])
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'),
            filters=[('NNAME', 'contains', '^B')])
        process = geo.UnionProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'union_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_disjoint(self):
        """
        Test DisjointProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'))
        process = geo.DisjointProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'difference_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_centroid(self):
        """
        Test CentroidProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        process = geo.CentroidProcess(inputs=[vector1_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'centroid_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_distance(self):
        """
        Test DistanceProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        process = geo.DistanceProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'distance_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_subset_raster(self):
        """
        Test SubsetProcess for vector & raster inputs
        """
        zipfile = ZipFile(os.path.join(testfile_path, '2states.zip'), 'r')
        zipfile.extract('2states.geojson', testfile_path)

        vector_io = VectorFileIO(
            uri=os.path.join(testfile_path, '2states.geojson'))
        raster_io = RasterFileIO(
            uri=os.path.join(testfile_path, 'globalairtemp.tif'))
        process = geo.SubsetProcess(inputs=[raster_io, vector_io])
        try:
            process.compute()
            self.assertEquals(type(process.output.data).__name__, 'Dataset')
            self.assertTrue(os.path.exists(process.output.uri))
            self.assertIsNotNone(process.id)
            self.assertIn(process.id, process.output.uri)
        finally:
            testfile = os.path.join(testfile_path, '2states.geojson')
            if os.path.exists(testfile):
                os.remove(testfile)
            if process:
                process.purge()

    def test_rastermath_add(self):
        """
        Test adding two rasters together
        """
        raster1_io = RasterFileIO(
            name='A', uri=os.path.join(testfile_path, 'globalairtemp.tif'))
        raster2_io = RasterFileIO(
            name='B', uri=os.path.join(testfile_path, 'globalprecip.tif'))
        calc = 'A + B'
        bands = [1, 1]

        process = geo.RasterMathProcess(
            inputs=[raster1_io, raster2_io], calc=calc, bands=bands)
        try:
            process.compute()
            self.assertTrue(os.path.exists(process.output.uri))
            oraster, raster1, raster2 = [x.read() for x in (
                process.output, raster1_io, raster2_io)]
            # Output raster should be same dimensions as raster 1
            self.assertEquals((oraster.RasterXSize, oraster.RasterYSize),
                              (raster1.RasterXSize, raster1.RasterYSize))
            orb, r1b, r2b = [x.GetRasterBand(1)
                             for x in (oraster, raster1, raster2)]
            # Min value of output should be >= the max minimum of inputs
            self.assertGreaterEqual(orb.GetStatistics(False, True)[0],
                                    max(r1b.GetStatistics(False, True)[0],
                                        r2b.GetStatistics(False, True)[0]))

            # Max value of output >=  max(minimum)+min(maximum) of inputs
            self.assertGreaterEqual(orb.GetStatistics(False, True)[1],
                                    max(r1b.GetStatistics(False, True)[0],
                                        r2b.GetStatistics(False, True)[0]) +
                                    min(r1b.GetStatistics(False, True)[1],
                                        r2b.GetStatistics(False, True)[1]))
        finally:
            if process:
                process.purge()

    def test_rastermath_multiply_by_value(self):
        """
        Test multiplying a raster by a value,
        and specifying output type (Float32)
        """
        raster1_io = RasterFileIO(
            name='A', uri=os.path.join(testfile_path, 'globalprecip.tif'))
        calc = 'A * 2'
        output_type = 'Float32'

        process = geo.RasterMathProcess(inputs=[raster1_io, ],
                                        calc=calc,
                                        output_type=output_type)
        try:
            process.compute()
            self.assertTrue(os.path.exists(process.output.uri))
            oraster, raster1 = [x.read() for x in (process.output, raster1_io)]
            # Output raster should be same dimensions as raster 1
            self.assertEquals((oraster.RasterXSize, oraster.RasterYSize),
                              (raster1.RasterXSize, raster1.RasterYSize))
            orb, r1b = [x.GetRasterBand(1) for x in (oraster, raster1)]
            # Maximum value of output should be 2x the max of input raster
            self.assertEqual(orb.GetStatistics(False, True)[1],
                             r1b.GetStatistics(False, True)[1] * 2)
            # Datatype of band should be Float32 (== gdal.GDT_Float32 == 6)
            self.assertEquals(6, orb.DataType)
            self.assertEquals(1.175494351E-38, orb.GetNoDataValue())

            # Each pixel of output raster should equal 2x input raster
            # unless it is a nodata value
            ora, r1a = [x.ReadAsArray() for x in (orb, r1b)]
            for x in range(raster1.RasterXSize):
                for y in range(raster1.RasterYSize):
                    if r1a[y, x] != r1b.GetNoDataValue():
                        self.assertEquals(ora[y, x], r1a[y, x] * 2)
        finally:
            if process:
                process.purge()

    def test_rastermath_logical_operators(self):
        """
        Test creation of a masked raster based on logical operators
        """
        raster1_io = RasterFileIO(
            name='A', uri=os.path.join(testfile_path, 'globalairtemp.tif'))
        calc = 'logical_or(logical_and(A >= 27000, A <= 28000), ' \
               'logical_and(A >= 30000, A <= 31000))'

        process = geo.RasterMathProcess(inputs=[raster1_io, ], calc=calc)
        try:
            process.compute()
            self.assertTrue(os.path.exists(process.output.uri))
            oraster, raster1 = [x.read() for x in (process.output, raster1_io)]
            # Output raster should be same dimensions as raster 1
            self.assertEquals((oraster.RasterXSize, oraster.RasterYSize),
                              (raster1.RasterXSize, raster1.RasterYSize))
            orb, r1b = [x.GetRasterBand(1) for x in (oraster, raster1)]
            # Maximum value of output should be 1
            self.assertEqual(orb.GetStatistics(False, True)[1], 1)
            # Minimum value of output should be 0
            self.assertEqual(orb.GetStatistics(False, True)[0], 0)
            # Pixels should be 1 where source is between 27K-28K or 30-31K
            ora, r1a = [x.ReadAsArray() for x in (orb, r1b)]
            self.assertTrue(ora[90, 10] == 1 and r1a[90, 10] == 30083)
            self.assertTrue(ora[160, 10] == 1 and r1a[160, 10] == 27074)
            # Pixels should be 0 where source is not between 27K-28K or 30-31K
            ora, r1a = [x.ReadAsArray() for x in (orb, r1b)]
            self.assertTrue(ora[120, 10] == 0 and r1a[120, 10] == 29623)
            self.assertTrue(ora[175, 10] == 0 and r1a[175, 10] == 23928)
        finally:
            if process:
                process.purge()

    def test_length(self):
        """
        Test LengthProcess for vector inputs
        """
        vector_roads = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_roads.geojson'),
            filters=[('type', '=', 'motorway'), ('bridge', '=', 1)])
        process = geo.LengthProcess(inputs=[vector_roads])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'length_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_area(self):
        """
        Test AreaProcess for vector inputs
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'),
            filters=[('NNAME', 'contains', '^B')])
        process = geo.AreaProcess(inputs=[vector1_io])
        try:
            process.compute()
            with open(os.path.join(
                    testfile_path,
                    'area_process_results.json')) as exp:
                expected_json = json.load(exp)
            actual_json = json.loads(process.output.read(
                format=geo.formats.JSON))
            self.assertEquals(len(expected_json['features']),
                              len(actual_json['features']))
        finally:
            if process:
                process.purge()

    def test_validationInputsPass(self):
        """
        Test the GaiaProcess.validate() function - pass on valid input
        """
        raster_io = RasterFileIO(uri='/fake/path')
        vector_io = VectorFileIO(uri='/fake/path')
        try:
            geo.ZonalStatsProcess(inputs=[raster_io, vector_io])
        except geo.GaiaException:
            self.fail("ZonalProcess should have passed validation but did not")

    def test_validationInputsOrder(self):
        """
        Test the GaiaProcess.validate() function - fail on incorrect order
        """
        raster_iO = RasterFileIO(uri='/fake/path1')
        vector_io = VectorFileIO(uri='/fake/path2')

        with self.assertRaises(geo.GaiaException) as ge:
            geo.ZonalStatsProcess(inputs=[vector_io, raster_iO])
        self.assertIn('Input #1 is of incorrect type.', str(ge.exception))

    def test_validationInputsMin(self):
        """
        Test the GaiaProcess.validate() function - fail on < minimum input types
        """

        vector_io = VectorFileIO(uri='/fake/path1')
        with self.assertRaises(geo.GaiaException) as ge:
            geo.IntersectsProcess(inputs=[vector_io])
        self.assertIn('Not enough inputs for process', str(ge.exception))

    def test_validationInputsNoMax(self):
        """
        Test the GaiaProcess.validate() function - pass on no max input types
        """

        raster_io1 = RasterFileIO(uri='/fake/path1')
        raster_io2 = RasterFileIO(uri='/fake/path2')

        try:
            geo.RasterMathProcess(inputs=[raster_io1, raster_io2], calc='A+B')
        except geo.GaiaException:
            self.fail("Multiple inputs should have passed validation")

    def test_validationInputsMax(self):
        """
        Test the GaiaProcess.validate() function - fail on > max input types
        """

        vector_io1 = VectorFileIO(uri='/fake/path')
        vector_io2 = VectorFileIO(uri='/fake/path')

        with self.assertRaises(geo.GaiaException) as ge:
            geo.LengthProcess(inputs=[vector_io1, vector_io2])
        self.assertIn('Incorrect # of inputs; expected 1', str(ge.exception))

    def test_mercator_geojson(self):
        vector_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals_3857.json'))
        self.assertEquals(vector_io.get_epsg(), 3857)
        jsonwm = json.loads(vector_io.read(format=geo.formats.JSON))
        self.assertEquals(jsonwm['crs']['properties']['name'], 'EPSG:3857')
        self.assertEquals(jsonwm['features'][0]['geometry']['coordinates'],
                          [4940150.544527022, 3941210.867854486])
        json84 = json.loads(vector_io.read(format=geo.formats.JSON, epsg=4326))
        self.assertEquals(json84['crs']['properties']['name'], 'EPSG:4326')
        self.assertEquals(json84['features'][0]['geometry']['coordinates'],
                          [44.378127400000004, 33.34517919999999])

    def test_nocrs_wgs84_geojson(self):
        vector_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals.geojson'))
        raw_json = json.loads(vector_io.read(format=geo.formats.JSON))
        self.assertFalse(hasattr(raw_json, 'crs'))
        epsg = vector_io.get_epsg()
        self.assertEquals(epsg, 4326)

    def test_nocrs_mercator_geojson(self):
        with open(os.path.join(testfile_path,
                               'iraq_hospitals_3857.json')) as injson:
            json3857 = json.load(injson)
        feature_io = FeatureIO(features=json3857['features'])
        epsg = feature_io.get_epsg()
        self.assertEquals(epsg, 3857)
        feature_json = feature_io.read(format=geo.formats.JSON)
        self.assertFalse(hasattr(feature_json, 'crs'))

    def test_within_reproject(self):
        """
        Test WithinProcess for vector inputs, where output should be in
        same projection as first input (in this case, 3857).
        """
        vector1_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'iraq_hospitals_3857.json'))
        vector2_io = VectorFileIO(
            uri=os.path.join(testfile_path, 'baghdad_districts.geojson'))
        process = geo.WithinProcess(inputs=[vector1_io, vector2_io])
        try:
            process.compute()
            self.assertEquals(process.output.data.crs, {'init': u'epsg:3857'})
            self.assertEquals(len(process.output.data), 19)
        finally:
            if process:
                process.purge()
