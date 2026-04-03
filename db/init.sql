CREATE TYPE p_types AS ENUM ('text', 'model');
CREATE TYPE dictionary_types AS ENUM(
    'DICT_4X4_50',
    'DICT_4X4_100',
    'DICT_4X4_250',
    'DICT_4X4_1000',
    'DICT_5X5_50',
    'DICT_5X5_100',
    'DICT_5X5_250',
    'DICT_5X5_1000',
    'DICT_6X6_50',
    'DICT_6X6_100',
    'DICT_6X6_250',
    'DICT_6X6_1000',
    'DICT_7X7_50',
    'DICT_7X7_100',
    'DICT_7X7_250',
    'DICT_7X7_1000'
);
CREATE TABLE markers (

    dictionary_name dictionary_types NOT NULL,
    marker_id SMALLINT,
    
    payload_type p_types NOT NULL,
    payload JSONB NOT NULL,

    PRIMARY KEY (dictionary_name, marker_id)
);
