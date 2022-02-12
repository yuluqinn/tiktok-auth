"""
Counter API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app, status
from service.routes import remove_counters

TEST_COUNTER = "foo"

######################################################################
#  T E S T   C A S E S
######################################################################
class CounterTest(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.testing = True

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        remove_counters()
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  T E S T   C A S E S 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_counters(self):
        """ Test Create a counter """
        resp = self.app.post("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["counter"], 0)

    def test_list_counters(self):
        """ Test List counters """
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        # create a counter and name sure it appears in the list
        self.app.post("/counters/foo")
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

    def test_read_counters(self):
        """ Test Read a counter """
        self.test_create_counters()
        resp = self.app.get("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["counter"], 0)

    def test_update_counters(self):
        """ Test Update a counter """
        self.test_read_counters()
        # now update it
        resp = self.app.put("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["counter"], 1)

    def test_delete_counters(self):
        """ Test Delete a counter """
        self.test_create_counters()
        resp = self.app.delete("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.app.get("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_counter_already_exists(self):
        """ Test counter already exists """
        self.test_create_counters()
        resp = self.app.post("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_unknown_counter(self):
        """ Test Update a counter that doesn't exist """
        resp = self.app.put("/counters/bar")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_reset_counter(self):
        """ Test Reset a counter """
        self.test_create_counters()
        # update counter to 3
        resp = self.app.put("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.put("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.put("/counters/{0}".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["counter"], 3)
        # reset counter to zero
        resp = self.app.put("/counters/{0}/reset".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["counter"], 0)

    def test_reset_unknown_counter(self):
        """ Test Reset a counter that doesn't exist """
        resp = self.app.put("/counters/{0}/reset".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed_handler(self):
        """ Test Method Not Allowed error handler """
        resp = self.app.get("/counters/{0}/reset".format(TEST_COUNTER))
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
