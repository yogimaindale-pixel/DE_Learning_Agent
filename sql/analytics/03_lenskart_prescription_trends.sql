-- Lenskart Prescription Analytics Star Schema Query
-- Analyzes vision lens distribution across single vision, bifocal, and progressive lens types by customer state.

SELECT 
    c.state,
    p.lens_type,
    COUNT(p.prescription_sk) AS total_prescriptions,
    ROUND(AVG(p.sphere_left), 2) AS avg_sphere_left,
    ROUND(AVG(p.sphere_right), 2) AS avg_sphere_right,
    ROUND(AVG(p.cylinder_left), 2) AS avg_cylinder_left,
    ROUND(AVG(p.cylinder_right), 2) AS avg_cylinder_right
FROM dim_prescription p
JOIN dim_customer c ON p.customer_id = c.customer_id AND c.is_current = 1
GROUP BY c.state, p.lens_type
ORDER BY total_prescriptions DESC;
