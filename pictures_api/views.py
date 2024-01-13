import os
from . import controller
from flask import Blueprint, request, make_response, jsonify

# Create a blueprint
bp = Blueprint('pictures', __name__, url_prefix='/')

@bp.post("/image")

def tag_image():
    
    # Check type of image
    if not request.is_json or "data" not in request.json:
        return make_response({"Description": "The picture must be in base64."}, 400)
    
    # Check and make sure that the confidence level for the tags is between 80 and 100
    min_confidence = request.args.get("min_confidence")
    
    # The default value is 80 if the confidence level is not specified
    if min_confidence is None:
        min_confidence = 80 
    else:
        min_confidence = int(min_confidence)
    
    # Get the image in base64
    imgb64str = request.json["data"]

    # Call the controller function and get tags for the picture with the given level of confidence    
    response = controller.tag_image(imgb64str, min_confidence)

    return jsonify(response), 200

@bp.get("/images")

def images():
    
    # Get the parameters from the request
    min_date = request.args.get('min_date')
    max_date = request.args.get('max_date')
    tags = request.args.get('tags')

    # Check if min_date or max_date is None
    if min_date is None or max_date is None:
    # Get all tags when min_date or max_date is None
        images_by_date = controller.images_by_date('1900-01-01 00:00:00','2100-12-31 23:59:00', tags)  
    else:
        # Call the controller function and get the images cosidering the query params    
        images_by_date = controller.images_by_date(min_date, max_date, tags)

    return jsonify(images_by_date), 200

@bp.get("/image/<image_id>")

def image(image_id):
    
    # Call the controller function and get the image with the given id
    image_download = controller.image_download(image_id)

    # Check if the image exists
    if image is None:
        return jsonify({'error': 'Image not found'}), 404

    return jsonify(image_download), 200

@bp.get("/tags")

def tags():
    
    # Get the parameters from the request
    min_date = request.args.get('min_date')
    max_date = request.args.get('max_date')

    # Check if min_date or max_date is None
    if min_date is None or max_date is None:
    # Get all tags when min_date or max_date is None
        tags = controller.get_all_tags('1900-01-01 00:00:00','2100-12-31 23:59:00')  
    else:
    # Call the controller function and get the tags considering the query params
        tags = controller.tags_list(min_date, max_date)

    return jsonify(tags), 200