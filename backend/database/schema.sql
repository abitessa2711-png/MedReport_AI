-- ============================================================
-- MedReport AI - MySQL schema
-- Run this once against an empty database, e.g.:
--   mysql -u root -p medreport_db < database/schema.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age INT NULL,
    gender VARCHAR(20) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,           -- 'pdf' | 'jpg' | 'png'
    report_date VARCHAR(50) NULL,             -- date printed on the report, if OCR found one
    raw_text LONGTEXT NULL,                   -- full OCR text dump
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded', -- uploaded | extracted | analyzed | failed
    error_message TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS extracted_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    value VARCHAR(50) NULL,          -- kept as string; not every OCR value is purely numeric
    numeric_value FLOAT NULL,        -- parsed numeric value when possible, used for charts
    unit VARCHAR(50) NULL,
    reference_range VARCHAR(100) NULL,
    status VARCHAR(20) NULL,         -- Normal | Low | High | Unknown
    was_corrected BOOLEAN NOT NULL DEFAULT FALSE, -- true if the user edited the OCR value
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT NOT NULL,
    overall_summary_en TEXT NULL,
    overall_summary_ta TEXT NULL,
    abnormal_findings_en TEXT NULL,
    abnormal_findings_ta TEXT NULL,
    normal_findings_en TEXT NULL,
    normal_findings_ta TEXT NULL,
    attention_points_en TEXT NULL,
    attention_points_ta TEXT NULL,
    ai_provider VARCHAR(50) NULL,
    ai_model VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_extracted_report ON extracted_results(report_id);
CREATE INDEX idx_analysis_report ON analysis_results(report_id);
