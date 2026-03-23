CREATE TABLE dictionaries (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TYPE p_types AS ENUM ('test', 'model');

CREATE TABLE markers (
    dictionary_id INT REFERENCES dictionaries(id),
    marker_id SMALLINT,
    
    payload_type p_types NOT NULL,
    payload VARCHAR(255) NOT NULL,

    PRIMARY KEY (dictionary_id, marker_id)
);
