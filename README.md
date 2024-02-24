# Microservices_Images

![Optional Alt Text](https://assets-global.website-files.com/643067b6b03b847eb9c418d0/648b215d9d6638f9da99b7a6_62f6bc9d4666f0a23ca506d4_tag_hero_preview.png)

## Description

The aim of this project is to collect, tag and store images that can be retrieved through a simple request using an MVC (Model-View-Controller) architecture for the API. The tagging of the images happens using Immaga. The images have to be given a public url endpoint so that they can be uploaded into Immaga for them to be tagged. As a default, tagging has been given an 80% confidence although it is a parameter that can be changed. Once the image is tagged, the endpoint from Imagekit is deleted and the endpoint stored in a relational database. Once tagged, the tags, date and unique id os the pictures are updated on the database. In this case, the normal form of the relational database is "broken" so that the user can access all the tags that have been attached to the image. The data in which the image has been uploaded is kept for further query either by date, tag, picture name or by picture id.

## Technologies and deployment

This APi has been built using Docker, Docker Compose, Immaga, Imagekit, MySQl, Waitresss and Flask. It can be easily deployed into AWS EC2 (with S3).

## Installation

This project uses Docker and Docker Compose to manage its services. To install and run the project, follow these steps:

1. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) if you haven't already.

2. Clone this repository: https://github.com/borjaregueral/Microservices_Images.git

3. Create a .env file in the root directory of the project, and set the following environment variables:

MYSQL_DATABASE=your_database
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
DB_HOST=db
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

4. Build and run the Docker containers: docker-compose up --build -d

## Usage

Use this api following these steps:

1. Post request with your image of choice
2. Get request (by image name, id, tag or date) to retrieve the image with the tagging.
3. Delete those images that are no longer of your interest

## Contributing
Contributions to Booking_Service are welcome! To contribute:

Fork the repository

Create a new branch: git checkout -b feature-branch-name
Make your changes

Push to the branch: git push origin feature-branch-name

Create a pull request

## License
The project Booking_Service is licensed under the MIT License.
: https://github.com/borjaregueral/Microservices_Images.git


3. Create a .env file in the root directory of the project, and set the following environment variables:

MYSQL_DATABASE=your_database
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
DB_HOST=db
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

4. Build and run the Docker containers: docker-compose up --build -d

## Usage

Use this api following these steps:

1. Post request with your image of choice
2. Get request (by image name, id, tag or date) to retrieve the image with the tagging.
3. Delete those images that are no longer of your interest

## Contributing
Contributions to Booking_Service are welcome! To contribute:

Fork the repository

Create a new branch: git checkout -b feature-branch-name
Make your changes

Push to the branch: git push origin feature-branch-name

Create a pull request

## License
The project Booking_Service is licensed under the MIT License.




