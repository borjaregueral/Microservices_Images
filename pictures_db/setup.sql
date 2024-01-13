
CREATE DATABASE IF NOT EXISTS Pictures;
USE Pictures;

CREATE TABLE pictures (
    id CHAR(36) PRIMARY KEY,
    path TEXT NOT NULL,
    date DATETIME NOT NULL
);

CREATE TABLE tags (
    tag VARCHAR(32),
    picture_id CHAR(36),
    confidence FLOAT NOT NULL,
    date DATETIME NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
