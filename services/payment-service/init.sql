CREATE TABLE IF NOT EXISTS payment_types (
    type_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
);

INSERT INTO payment_types (type_id, name) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'online'),
    ('550e8400-e29b-41d4-a716-446655440002', 'manual')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) UNIQUE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    payment_type_id VARCHAR(36) REFERENCES payment_types(type_id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);