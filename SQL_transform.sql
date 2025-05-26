-- Odstránenie duplicitných záznamov
WITH deduplicated AS (
    SELECT 
        id,
        name,
        email,
        date,
        amount,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY id) AS row_num
    FROM 
        "manual-input"."csv_input"
)
SELECT 
    id,
    name,
    COALESCE(email, 'unknown@example.com') AS email,
    TO_DATE(date, 'YYYY-MM-DD') AS date,
    ABS(amount) AS amount
FROM 
    deduplicated
WHERE 
    row_num = 1;