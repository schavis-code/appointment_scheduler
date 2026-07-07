CREATE DATABASE IF NOT EXISTS appointments;
USE appointments;

DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS hairdressers;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hairdressers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    hairdresser_id BIGINT NOT NULL,
    service_id BIGINT NOT NULL,
    appointment_start DATETIME NOT NULL,
    appointment_end DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_appointments_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id),

    CONSTRAINT fk_appointments_hairdresser
        FOREIGN KEY (hairdresser_id) REFERENCES hairdressers(id),

    CONSTRAINT fk_appointments_service
        FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE INDEX idx_appointments_start
ON appointments (appointment_start);

CREATE INDEX idx_appt_hairdresser_start
ON appointments (hairdresser_id, appointment_start);
