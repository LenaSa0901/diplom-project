-- Таблица основная
CREATE TABLE IF NOT EXISTS applicants (
    id SERIAL PRIMARY KEY,
    applicant_id VARCHAR(20) NOT NULL,   
    position INT,
    total_balls INT,
    individual_achievements_balls INT,
    enrollment_agreement BOOLEAN,
    priority INT,
    need_hostel BOOLEAN,
    benefit VARCHAR(50),
    main_highest_priority VARCHAR(255),
    contest_group_id INT NOT NULL,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(applicant_id, contest_group_id, load_date)
);

-- Таблица баллов по предметам
CREATE TABLE IF NOT EXISTS subject_scores (
    id SERIAL PRIMARY KEY,
    applicant_id VARCHAR(20) NOT NULL,   
    contest_group_id INT NOT NULL,
    subject_name VARCHAR(100),
    subject_id INT,
    ball INT,
    priority INT,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id, contest_group_id, load_date) 
        REFERENCES applicants(applicant_id, contest_group_id, load_date)
);

-- Индексы
CREATE INDEX idx_applicants_id ON applicants(applicant_id);
CREATE INDEX idx_applicants_position ON applicants(position);