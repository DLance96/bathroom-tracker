CREATE DATABASE bathroom_tracker;
CREATE USER bathroom PASSWORD 'bath';
GRANT ALL ON DATABASE bathroom_tracker TO bathroom;
CREATE TABLE major (
    mid SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);
CREATE TABLE building (
    bid SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    opens TIME WITHOUT TIME ZONE,
    closes TIME WITHOUT TIME ZONE
);
CREATE TABLE building_access (
    bid SERIAL REFERENCES building(bid),
    mid INTEGER REFERENCES major(mid),
    PRIMARY KEY (bid, mid)
);
CREATE TABLE person (
    case_id VARCHAR(8) PRIMARY KEY,
    mid INTEGER REFERENCES major(mid),
    last_seen TIMESTAMP WITHOUT TIME ZONE
);
CREATE TYPE gender AS ENUM ('male', 'female', 'neither');
CREATE TABLE bathroom (
    brid SERIAL PRIMARY KEY,
    bid INTEGER REFERENCES building(bid) NOT NULL,
    floor INTEGER,
    gender gender
);
CREATE TABLE review (
    rid SERIAL PRIMARY KEY,
    brid INTEGER REFERENCES bathroom(brid),
    review TEXT,
    case_id VARCHAR(8) REFERENCES person(case_id),
    rating INTEGER CHECK (rating > 0 AND rating <= 5),
    time_added TIMESTAMP WITHOUT TIME ZONE
);
