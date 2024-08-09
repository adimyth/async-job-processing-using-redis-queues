-- Step 1: Create the 'auth' schema (if not already created)
CREATE SCHEMA IF NOT EXISTS auth;

-- Step 2: Create the 'users' table inside the 'auth' schema with additional fields
CREATE TABLE auth.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    department VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Insert 15 users with realistic values into the 'users' table
INSERT INTO
    auth.users (
        username,
        email,
        password_hash,
        age,
        salary,
        department
    )
VALUES
    (
        'jdoe',
        'jdoe@example.com',
        'hash12345',
        28,
        70000.00,
        'Engineering'
    ),
    (
        'asmith',
        'asmith@example.com',
        'hash23456',
        35,
        85000.00,
        'Marketing'
    ),
    (
        'mjones',
        'mjones@example.com',
        'hash34567',
        40,
        95000.00,
        'Sales'
    ),
    (
        'lwilson',
        'lwilson@example.com',
        'hash45678',
        30,
        65000.00,
        'HR'
    ),
    (
        'kbrown',
        'kbrown@example.com',
        'hash56789',
        50,
        120000.00,
        'Finance'
    ),
    (
        'tjohnson',
        'tjohnson@example.com',
        'hash67890',
        27,
        68000.00,
        'Engineering'
    ),
    (
        'dlee',
        'dlee@example.com',
        'hash78901',
        42,
        105000.00,
        'Marketing'
    ),
    (
        'wclark',
        'wclark@example.com',
        'hash89012',
        45,
        98000.00,
        'Sales'
    ),
    (
        'arodriguez',
        'arodriguez@example.com',
        'hash90123',
        33,
        72000.00,
        'HR'
    ),
    (
        'tlopez',
        'tlopez@example.com',
        'hash01234',
        29,
        110000.00,
        'Finance'
    ),
    (
        'jmartin',
        'jmartin@example.com',
        'hash12346',
        37,
        83000.00,
        'Engineering'
    ),
    (
        'cwhite',
        'cwhite@example.com',
        'hash23457',
        41,
        90000.00,
        'Marketing'
    ),
    (
        'bperez',
        'bperez@example.com',
        'hash34568',
        38,
        75000.00,
        'Sales'
    ),
    (
        'nlewis',
        'nlewis@example.com',
        'hash45679',
        36,
        69000.00,
        'HR'
    ),
    (
        'mpatel',
        'mpatel@example.com',
        'hash56780',
        47,
        130000.00,
        'Finance'
    );