--
-- File generated with SQLiteStudio v3.3.3 on Κυρ Ιουν 6 22:36:56 2021
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: address
DROP TABLE IF EXISTS address;

CREATE TABLE address (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    street      VARCHAR (50) NOT NULL,
    number      VARCHAR (5)  NOT NULL,
    postcode    VARCHAR (10) NOT NULL,
    customer_id INTEGER      NOT NULL
                             REFERENCES customer (id)
);

-- Table: customer
DROP TABLE IF EXISTS customer;

CREATE TABLE customer (
    id        INTEGER      PRIMARY KEY AUTOINCREMENT,
    firstname VARCHAR (50) NOT NULL,
    lastname  VARCHAR (50) NOT NULL,
    phone     VARCHAR (15)
);

-- Table: order
DROP TABLE IF EXISTS [order];

CREATE TABLE [order] (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    date        DATETIME     NOT NULL
                             DEFAULT (CURRENT_TIMESTAMP),
    status      VARCHAR (10) NOT NULL,
    customer_id INTEGER      REFERENCES customer (id)
                             NOT NULL
);

-- Table: order_item
DROP TABLE IF EXISTS order_item;

CREATE TABLE order_item (
    order_id   INTEGER REFERENCES [order] (id)
                       NOT NULL,
    product_id INTEGER REFERENCES product (id)
                       NOT NULL,
    quantity   INTEGER NOT NULL
                       DEFAULT (0)
);

-- Table: product
DROP TABLE IF EXISTS product;

CREATE TABLE product (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT    NOT NULL,
    description         TEXT    NOT NULL,
    price               REAL    NOT NULL,
    discount_ratio      REAL    DEFAULT (0)
                                NOT NULL,
    stock               INTEGER NOT NULL,
    is_hot              INTEGER DEFAULT (0),
    product_category_id TEXT    REFERENCES product_category (id)
);

-- Table: product_category
DROP TABLE IF EXISTS product_category;

CREATE TABLE product_category (
    id     TEXT    PRIMARY KEY,
    title  TEXT    NOT NULL,
    parent TEXT,
    other  INTEGER DEFAULT (0)
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
