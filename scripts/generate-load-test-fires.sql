\set ON_ERROR_STOP on

UPDATE fires
SET deleted_at = NULL
WHERE external_card_number LIKE 'LOADTEST-20260810-%';

WITH
config AS (
    SELECT 10000::integer AS target_count
),
existing AS (
    SELECT count(*)::integer AS count
    FROM fires
    WHERE external_card_number LIKE 'LOADTEST-20260810-%'
),
reference_ids AS (
    SELECT
        ARRAY(SELECT id FROM municipalities ORDER BY id) AS municipalities,
        ARRAY(SELECT id FROM land_types ORDER BY id) AS land_types,
        ARRAY(SELECT id FROM forestries ORDER BY id) AS forestries,
        ARRAY(SELECT id FROM reasons ORDER BY id) AS reasons
),
source_rows AS (
    SELECT
        series.number,
        refs.*
    FROM config
    CROSS JOIN existing
    CROSS JOIN reference_ids refs
    CROSS JOIN LATERAL generate_series(existing.count + 1, config.target_count) AS series(number)
)
INSERT INTO fires (
    fire_date,
    time_msg,
    end_time,
    is_forest,
    land_type_id,
    area,
    address,
    municipality_id,
    latitude,
    longitude,
    forestry_id,
    reason_id,
    right_of_way,
    right_of_way_type,
    owner,
    source,
    extra,
    creator_id,
    reviewer_id,
    external_card_number,
    status,
    deleted_at
)
SELECT
    CURRENT_DATE - ((number * 37) % 365),
    date_trunc('day', now() - make_interval(days => ((number * 37) % 365)))
        + make_interval(hours => 7 + (number % 14), mins => (number * 11) % 60),
    CASE WHEN number % 3 = 2 THEN
        date_trunc('day', now() - make_interval(days => ((number * 37) % 365)))
            + make_interval(hours => 10 + (number % 12), mins => (number * 17) % 60)
    END,
    number % 2 = 0,
    CASE WHEN cardinality(land_types) > 0 THEN land_types[1 + ((number - 1) % cardinality(land_types))] END,
    round((((number * 17) % 750) + ((number % 100) / 100.0))::numeric, 2),
    'Нагрузочный тест, пожар #' || number,
    CASE WHEN cardinality(municipalities) > 0 THEN municipalities[1 + ((number - 1) % cardinality(municipalities))] END,
    NULL,
    NULL,
    CASE
        WHEN number % 2 = 0 AND cardinality(forestries) > 0
        THEN forestries[1 + ((number - 1) % cardinality(forestries))]
    END,
    CASE WHEN cardinality(reasons) > 0 THEN reasons[1 + ((number - 1) % cardinality(reasons))] END,
    number % 5 = 0,
    CASE WHEN number % 5 = 0 THEN 'охранная зона железных дорог' END,
    CASE number % 4
        WHEN 0 THEN 'Муниципальная собственность'
        WHEN 1 THEN 'Федеральная собственность'
        WHEN 2 THEN 'Частная собственность (в т.ч. КФХ, ИП и т.д.)'
        ELSE 'Вид формы собственности не установлен или отсутствует'
    END,
    'Синтетические данные нагрузочного теста',
    'Можно скрыть скриптом scripts/hide-load-test-fires.sql',
    1,
    CASE WHEN number % 3 = 0 THEN NULL ELSE 1 END,
    'LOADTEST-20260810-' || lpad(number::text, 5, '0'),
    CASE number % 3
        WHEN 0 THEN 'OPEN'
        WHEN 1 THEN 'IN_REVIEW'
        ELSE 'COMPLETED'
    END,
    NULL
FROM source_rows;

-- Assign addresses and points inside actual municipality polygons with:
-- python scripts/assign-load-test-locations.py client-web/public/data/orenburg-municipalities.geojson |
--   docker exec -i fire_postgres psql -U fire_user -d fire_db

SELECT
    count(*) AS load_test_fires,
    count(*) FILTER (WHERE deleted_at IS NULL) AS active_load_test_fires
FROM fires
WHERE external_card_number LIKE 'LOADTEST-20260810-%';
