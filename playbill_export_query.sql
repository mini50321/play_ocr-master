SELECT 
    p.id AS person_id,
    p.name AS person_name,
    c.category,
    c.role,
    s.id AS show_id,
    s.title AS show_title,
    prod.year AS production_year,
    t.name AS theater_name,
    c.is_equity AS equity_flag,
    prod.start_date,
    prod.end_date
FROM 
    credit c
    INNER JOIN person p ON c.person_id = p.id
    INNER JOIN production prod ON c.production_id = prod.id
    INNER JOIN show s ON prod.show_id = s.id
    INNER JOIN theater t ON prod.theater_id = t.id
ORDER BY 
    p.name, s.title, prod.year;

