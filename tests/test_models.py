# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()

        new_price = 10.0
        product.price = new_price
        product.update()

        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.price, new_price)

    def test_delete_a_product(self):
        product = ProductFactory()

        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_product(self):
        products = Product.all()
        self.assertEqual(len(products), 0)

        for i in range(5):
            product = ProductFactory()
            product.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        for i in range(5):
            product = ProductFactory()
            product.create()

        products = Product.all()
        target = products[0].name

        expected_matches = sum(1 for p in products if p.name == target)

        search_results = Product.find_by_name(target)
        self.assertEqual(search_results.count(), expected_matches)

        for p in search_results:
            self.assertEqual(p.name, target)

    def test_find_product_by_availability(self):

        expected_matches = 0
        target = None

        for i in range(10):
            product = ProductFactory()
            product.create()

            if i == 0:
                target = product.available

            if target == product.available:
                expected_matches += 1

        search_results = Product.find_by_availability(target)
        self.assertEqual(search_results.count(), expected_matches)

        for p in search_results:
            self.assertEqual(p.available, target)

    def test_find_product_by_price(self):

        expected_matches = 0
        target = None

        for i in range(10):
            product = ProductFactory()
            product.create()

            if i == 0:
                target = product.price

            if target == product.price:
                expected_matches += 1

        search_results = Product.find_by_price(target)
        self.assertEqual(search_results.count(), expected_matches)

        for p in search_results:
            self.assertEqual(p.price, target)

    def test_find_product_by_category(self):

        expected_matches = 0
        target = None

        for i in range(10):
            product = ProductFactory()
            product.create()

            if i == 0:
                target = product.category

            if target == product.category:
                expected_matches += 1

        search_results = Product.find_by_category(target)
        self.assertEqual(search_results.count(), expected_matches)

        for p in search_results:
            self.assertEqual(p.category, target)

    def test_serialize_deserialize(self):
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)

        tmp_dict = product.serialize()
        product2 = Product().deserialize(tmp_dict)

        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product2 is not None)
        self.assertEqual(product.id, product2.id)
        self.assertEqual(product.name, product2.name)
        self.assertEqual(product.description, product2.description)
        self.assertEqual(product.available, product2.available)
        self.assertEqual(product.price, product2.price)
        self.assertEqual(product.category, product2.category)

        tmp_dict_defective = tmp_dict.copy()
        tmp_dict_defective["available"] = "Yes"
        with self.assertRaises(DataValidationError):
            Product().deserialize(tmp_dict_defective)

        tmp_dict_defective = tmp_dict.copy()
        del tmp_dict_defective["price"]
        with self.assertRaises(DataValidationError):
            Product().deserialize(tmp_dict_defective)

        tmp_dict_defective = str(tmp_dict)
        with self.assertRaises(DataValidationError):
            Product().deserialize(tmp_dict_defective)
