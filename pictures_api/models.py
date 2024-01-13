import os
import base64
from datetime import datetime
from sqlalchemy import create_engine, text

# When running locally there is no need but when running in a container we need to set the environment variables
# Get the database user from the environment variables
db_user = os.getenv('DB_USER')

# Get the database password from the environment variables
db_password = os.getenv('DB_PASSWORD')

# Get the database host from the environment variables
db_host = os.getenv('DB_HOST')

# Get the database name from the environment variables
db_name = os.getenv('DB_NAME')

# Create a SQLAlchemy engine that will connect to the MySQL database
# Using the user, password, host, and database name provided in the dockerfile as environment variables
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}')


def pictures_and_tags(response):
    
    # Extract the parameters from the response dictionary
    id = response['id']
    data_img = response['data']
    size = response['size']
    path = response['path']
    date = response['date']
    tags = response['tags']

    # Insert into Pictures table
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO pictures (id, path, date)
            VALUES (:id, :path, :date)
        """), {'id': id, 'path': path, 'date': date})
        conn.commit()

    # Print the tags
    print(tags) 
    
    # Insert into Tags table
    for tag in tags:
        confidence = int(tag['confidence'])
        tag_name = tag['tag']
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO tags (tag, picture_id, confidence, date)
                VALUES (:tag, :picture_id, :confidence, :date)
            """), {'tag': tag_name, 'picture_id': id, 'confidence': confidence, 'date': date})
            conn.commit()
    
    # Create the characteristics dictionary with the parameters to obtain in the request                  
    characteristics = {
        "id": id,
        "size": size,
        "date": date,
        "tags": tags,
        "data": data_img
    }
    
    return characteristics
    
def get_images(min_date, max_date, tags):

    # Creta an empty list of images
    images = []
    
    # Query the database
    with engine.connect() as conn:
       
        # Generate the IN clause based on the number of tags and group_concat to have a list of tags and confidences
        # As an independent list of tags gives issues as uploads each file the "number fo tags" to the database
        # The solution is to use a group_concat to have a list of tags and confidences
        tag_clause = f"({','.join([f':tag{i}' for i in range(len(tags))])})" if tags else "(NULL)"
        result_get_images = conn.execute(text("""
            SELECT pictures.id, pictures.date, pictures.path,
                   GROUP_CONCAT(tags.tag) as tags,
                   GROUP_CONCAT(tags.confidence) as confidences
            FROM pictures
            LEFT JOIN tags ON pictures.id = tags.picture_id
            WHERE (:min_date IS NULL OR pictures.date >= :min_date) AND
                  (:max_date IS NULL OR pictures.date <= :max_date) AND
                  tags.tag IN """ + tag_clause + """
            GROUP BY pictures.id
        """),{'min_date': min_date, 'max_date': max_date, **{'tag'+str(i): tag for i, tag in enumerate(tags)}}).fetchall()

    return result_get_images

def get_image(image_id):
    
    # Query the database
    with engine.connect() as conn:
        # Get images with the specified id
        # Only need to get one image as the id is unique
        result_get_image = conn.execute(text("""
            SELECT pictures.id, pictures.date, pictures.path,
                   GROUP_CONCAT(tags.tag) as tags,
                   GROUP_CONCAT(tags.confidence) as confidences
            FROM pictures
            LEFT JOIN tags ON pictures.id = tags.picture_id
            WHERE pictures.id = :image_id
            GROUP BY pictures.id
        """), {'image_id': image_id}).fetchone()

    return result_get_image

def get_tags(min_date, max_date):
    
    # Query the database
    with engine.connect() as conn:
        # Get the tags with the specified date range
        # Get all images as there is a range of 
        result_get_tags = conn.execute(text("""
            SELECT tags.tag, COUNT(pictures.id) as n_images, 
                   MIN(tags.confidence) as min_confidence, 
                   MAX(tags.confidence) as max_confidence, 
                   AVG(tags.confidence) as mean_confidence
            FROM pictures
            LEFT JOIN tags ON pictures.id = tags.picture_id
            WHERE (pictures.date >= :min_date OR :min_date IS NULL) AND 
                  (pictures.date <= :max_date OR :max_date IS NULL)
            GROUP BY tags.tag
        """), {'min_date': min_date, 'max_date': max_date}).fetchall()

    # Convert the result to a list of dictionaries
    tags_result = [{'tag': row[0], 
                    'n_images': row[1],
                    'min_confidence': row[2], 
                    'max_confidence': row[3], 
                    'mean_confidence': row[4]} 
                   for row in result_get_tags]

    return tags_result