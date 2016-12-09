CREATE DATABASE bathroom_tracker;
CREATE USER bathroom PASSWORD 'bath';
GRANT ALL ON DATABASE bathroom_tracker TO bathroom;
CREATE TABLE major (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);
CREATE TABLE building (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    opens TIME WITHOUT TIME ZONE,
    closes TIME WITHOUT TIME ZONE
);
CREATE TABLE building_access (
    building SERIAL REFERENCES building(id),
    major INTEGER REFERENCES major(id),
    PRIMARY KEY (building, major)
);
CREATE TABLE person (
    case_id VARCHAR(8) PRIMARY KEY,
    major INTEGER REFERENCES major(id),
    last_seen TIMESTAMP WITHOUT TIME ZONE
);
CREATE TYPE gender AS ENUM ('male', 'female', 'neither');
CREATE TABLE bathroom (
    id SERIAL PRIMARY KEY,
    building INTEGER REFERENCES building(id) NOT NULL,
    floor INTEGER,
    gender gender
);
CREATE TABLE review (
    id SERIAL PRIMARY KEY,
    bathroom INTEGER REFERENCES bathroom(id),
    review TEXT,
    person VARCHAR(8) REFERENCES person(case_id),
    rating INTEGER CHECK (rating > 0 AND rating <= 5)
);
