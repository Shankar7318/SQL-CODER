-- init.sql - Optional sample data
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER,
    salary DECIMAL(10,2),
    city VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email, first_name, last_name, age, salary, city, country) VALUES
('john_doe', 'john@example.com', 'John', 'Doe', 28, 75000, 'New York', 'USA'),
('jane_smith', 'jane@example.com', 'Jane', 'Smith', 32, 82000, 'Los Angeles', 'USA'),
('bob_wilson', 'bob@example.com', 'Bob', 'Wilson', 45, 95000, 'Chicago', 'USA');