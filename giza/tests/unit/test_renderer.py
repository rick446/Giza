import json
from unittest import TestCase

import mock

from giza import render

class TestJSONRenderer(TestCase):

    def setUp(self):
        self.system = dict(
            request=mock.Mock(
                response=mock.Mock(
                    content_type='text/html')))
        self.renderer = render.JSONRenderer(None)

    def test_simple(self):
        value = dict(a=5)
        self.assertEqual(
            self.renderer(value, self.system),
            json.dumps(value))

    def test_with_custom_json(self):
        value = mock.Mock(
            __json__=lambda: dict(a=10))
        self.assertEqual(
            self.renderer(value, self.system),
            '{"a": 10}')

    def test_invalid(self):
        value = mock.Mock()
        self.assertRaises(
            TypeError, self.renderer, value, self.system)

