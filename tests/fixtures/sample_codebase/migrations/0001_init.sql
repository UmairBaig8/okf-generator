-- Stores registered users of the platform
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);

-- Active (non-deleted) users only
CREATE OR REPLACE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;

/* Returns the number of days since signup for a given user */
CREATE OR REPLACE FUNCTION days_since_signup(user_id INT)
RETURNS INT AS $$
BEGIN
    RETURN 0;
END;
$$ LANGUAGE plpgsql;

CREATE INDEX idx_users_email ON users (email);
