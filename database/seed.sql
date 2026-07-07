USE appointments;

INSERT INTO services (
    name,
    description,
    duration_minutes,
    price,
    active
) VALUES
    ('Haircut', 'Basic haircut service', 60, 50.00, TRUE),
    ('Hair Coloring', 'Complete hair coloring', 120, 75.00, TRUE),
    ('Shampoo and Style', 'Shampoo and styling service', 30, 35.00, TRUE);

INSERT INTO hairdressers (
    first_name,
    last_name,
    email,
    active
) VALUES
    ('Hairdresser', 'One', 'hairdresser.one@example.com', TRUE),
    ('Hairdresser', 'Two', 'hairdresser.two@example.com', TRUE);

INSERT INTO customers (
    first_name,
    last_name,
    email,
    phone
) VALUES
    ('Taylor', 'Example', 'taylor@example.com', '+15550101010'),
    ('Jordan', 'Example', 'jordan@example.com', '+15550101011');

INSERT INTO appointments (
    customer_id,
    hairdresser_id,
    service_id,
    appointment_start,
    appointment_end,
    status,
    notes
) VALUES
    (1, 1, 1, '2030-01-02 10:00:00', '2030-01-02 11:00:00', 'scheduled', 'Sample haircut appointment'),
    (2, 2, 3, '2030-01-02 13:00:00', '2030-01-02 13:30:00', 'confirmed', 'Sample shampoo and style appointment');
