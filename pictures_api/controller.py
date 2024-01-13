import os
import io
import json
import uuid
import base64
import datetime
import requests
from PIL import Image
from flask import request
from datetime import datetime
from imagekitio import ImageKit
from . import models

# Set the path to the credentials file in the container
BASE = "/pictures_api"
credentials_file = f"{BASE}/credentials.json"

def get_credentials():
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
    return credentials

def credentials_imagekit():
    #Upload credentials for imagekit
    credentials = get_credentials()["imagekit"]
    imagekit = ImageKit(
    credentials["public_key"],
    credentials["private_key"],
    credentials["url_endpoint"]
    )
    return imagekit

def credentials_imagga():  
    credentials = get_credentials()["imagga"]
    api_key = credentials["api_key"]
    api_secret = credentials["api_secret"]
    return api_key, api_secret


def image_info(data):

    # Generate a unique ID for the image
    # Call the function only ones or the ID will lose consistency
    image_id = str(uuid.uuid4())
    
    # Get the size of the image in KB
    image_size = round(len(data) / 1024, 4)

    # Convert the size to a string and add "KB"
    image_size_str = str(image_size) + " KB"

    # Create a dictionary with the image information
    identifier = {
        "id": image_id,
        "size": image_size_str,
        "data": data,
    }
    
    return identifier
    

def upload_image(image_info_data):
    
    # Credentials for imagekit
    imagekit = credentials_imagekit()

    # Save the image object as a jpg file
    file_name = f"{image_info_data['id']}.jpg"

    # Upload the jpg file to ImageKit
    image_data = image_info_data["data"]
    upload_info = imagekit.upload(file=image_data, file_name=file_name)
    
    #Public url of the image
    image_url = upload_info.url
    file = upload_info.file_id
    
    # Date when the image was uploaded
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a dictionary with the information    
    data_image_file = {
        "id": image_info_data['id'],
        "date": upload_date,
        "image_url": image_url,
        "file": file,
        "file_name": file_name
    }
    
    return data_image_file

def save_file(image_info_data):
    # Decode the base64 data to bytes
    image_data = base64.b64decode(image_info_data["data"])

    # Get the directory of the Docker volume
    image_storage_directory = '/app/images'
    
    # Specify the relative directory to save the image
    relative_directory = "saved_images"
    
    # Generate a unique filename for the image
    filename = image_info_data['id'] + ".jpg"

    # Create the full file path
    file_path = os.path.join(image_storage_directory, relative_directory, filename)

    # Create the directories if they don't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the bytes to a file
    with open(file_path, 'wb') as f:
        f.write(image_data)
    
    return file_path

def tag_image(data, min_confidence=80):
    
    # Get the image information
    image_info_data = image_info(data)
    image_id = image_info_data["id"]
    
    # Credentials for imagekit
    imagekit = credentials_imagekit()
    
    # Call upload_image once and store the result
    upload_info = upload_image(image_info_data)
    
    # Get the image URL and file ID
    image_url = upload_info["image_url"]
    file = upload_info["file"]
    
    # Call the Imagga API
    response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url}", auth=(credentials_imagga()[0], credentials_imagga()[1]))
    
    # Check if the request was successful
    if response.status_code != 200:
        print(response.content)  # Print the response content
        raise Exception(f"Imagga API request failed with status code {response.status_code}")
    
    # Check if 'result' is in the response
    if 'result' not in response.json():
        raise Exception("The key 'result' was not found in the Imagga API response")
    
    # Check if 'tags' is in the response
    image_tags = [
        {
            "tag": t["tag"]["en"],
            "confidence": round(t["confidence"], 2)
        }
        for t in response.json()["result"]["tags"]
        if t["confidence"] > min_confidence
    ]
    
    imagekit.delete_file(file_id = file)
    
    # Check if the image is deleted
    # try to retrieve the image
    try:
        file_details = imagekit.get_file_details(file_id = file)
    except Exception as e:
        file_details = None

    # Check if the image is deleted
    if file_details is None:
        print("The image is deleted successfully.")
    else:
        print("The image is not deleted.")
    
    # Create a dictionary with the image information
    response = {
        "id": image_id,
        "size": image_info_data["size"],
        "date": upload_info["date"],
        "tags": [{"tag": tag['tag'], "confidence": tag['confidence']} for tag in image_tags],
        "data": image_info_data["data"],
        "path": save_file(image_info_data)
    }

    # Take response to the database
    return models.pictures_and_tags(response)


def images_by_date(min_date, max_date, tags):
    
    # Convert tags from comma-separated string to list
    if isinstance(tags, str):
        tags = tags.split(',')

    # Query the database
    images_query = models.get_images(min_date, max_date, tags)

    # Convert the result to JSON
    images_json = [
        {
            'id': image.id,
            'date': image.date.strftime('%Y-%m-%d %H:%M:%S'),
            'size': str(round(os.path.getsize(image.path) / 1024 , 4)) + ' KB', 
            'tags': [
                {'tag': tag, 'confidence': confidence} 
                for tag, confidence in zip(image.tags.split(','), image.confidences.split(','))
            ]
        } 
        for image in images_query
    ]

    return images_json

def image_download(image_id):
    
    # Query the database
    image_down = models.get_image(image_id)
    
    # Check if the image exists
    if image_down is None:
        return None

    # Read the image file
    with open(image_down.path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Convert the result to JSON
    image_down_json = {
        'id': image_down.id,
        'date': image_down.date.strftime('%Y-%m-%d %H:%M:%S'),
        'size': str(round(os.path.getsize(image_down.path) / 1024 , 4)) + ' KB',
        'tags': [
            {'tag': tag, 'confidence': confidence} 
            for tag, confidence in zip(image_down.tags.split(','), image_down.confidences.split(','))
        ],
        'data': image_data
    }
    
    return image_down_json

def tags_list(min_date, max_date):
    
    # Query the database to get list of tags
    tags_list = models.get_tags(min_date, max_date)

    return tags_list