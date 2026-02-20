CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    ai_task_id VARCHAR(255),
    ai_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhook_logs_received_at ON webhook_logs(received_at);
CREATE INDEX idx_webhook_logs_processed ON webhook_logs(processed);

CREATE TABLE IF NOT EXISTS ai_responses (
    id SERIAL PRIMARY KEY,
    log_id INTEGER REFERENCES webhook_logs(id),
    response_data JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);