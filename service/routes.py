######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    location_url = url_for("get_product", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

#
# PLACE YOUR CODE TO LIST ALL PRODUCTS HERE
#
@app.route("/products", methods=["GET"])
def get_products():
    avai = request.args.get('available', default=None, type=str)
    name = request.args.get('name', default=None, type=str)
    cate = request.args.get('category', default=None, type=str)

    app.logger.info("GET /products %s", request.args)

    if cate is not None:
        if cate.isdigit():
            cate = int(cate)
            cate = Category(cate)  # lookup by int value
        else:
            cate = Category[cate]  # lookup by name

        products = Product.find_by_category(cate)
    elif avai is not None:
        if avai.lower() in ["true", "yes", "1"]:
            avai = True
        else:
            avai = False
        products = Product.find_by_availability(avai)
    elif name is not None:
        products = Product.find_by_name(name)
    else:
        products = Product.all()

    msg = [p.serialize() for p in products]
    return jsonify(msg), status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################

#
# PLACE YOUR CODE HERE TO READ A PRODUCT
#

@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):

    product = Product.find(product_id)
    app.logger.info("GET /products/<product_id> %s", product_id)

    if product is None:
        app.logger.info("GET /products/<product_id> %s not found", product_id)
        abort(
            status.HTTP_404_NOT_FOUND,
            "No said product",
        )

    msg = product.serialize()
    return jsonify(msg), status.HTTP_200_OK

######################################################################
# U P D A T E   A   P R O D U C T
######################################################################
#
# PLACE YOUR CODE TO UPDATE A PRODUCT HERE
#


@app.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):

    product = Product.find(product_id)
    app.logger.info("PUT /products/<product_id> %s", product_id)

    if product is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            "No said product",
        )

    check_content_type("application/json")
    data = request.get_json()

    product.deserialize(data)  # FIXME: no error check
    product.id = product_id
    product.update()

    msg = product.serialize()
    return jsonify(msg), status.HTTP_200_OK


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################


#
# PLACE YOUR CODE TO DELETE A PRODUCT HERE
#
@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):

    product = Product.find(product_id)

    if product is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            "No said product",
        )

    product.delete()

    return "OK", status.HTTP_204_NO_CONTENT


# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     app.logger.info('You want path: %s', path)
#     return 'You want path: %s' % path, status.HTTP_404_NOT_FOUND