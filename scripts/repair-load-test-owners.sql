\set ON_ERROR_STOP on

UPDATE fires
SET owner = CASE substring(external_card_number FROM '([0-9]+)$')::integer % 4
    WHEN 0 THEN 'Муниципальная собственность'
    WHEN 1 THEN 'Федеральная собственность'
    WHEN 2 THEN 'Частная собственность (в т.ч. КФХ, ИП и т.д.)'
    ELSE 'Вид формы собственности не установлен или отсутствует'
END
WHERE external_card_number LIKE 'LOADTEST-20260810-%';

UPDATE fires
SET right_of_way_type = CASE
    WHEN right_of_way THEN 'охранная зона железных дорог'
    ELSE NULL
END
WHERE external_card_number LIKE 'LOADTEST-20260810-%';

UPDATE fires
SET source = 'Синтетические данные нагрузочного теста',
    extra = 'Можно скрыть скриптом scripts/hide-load-test-fires.sql'
WHERE external_card_number LIKE 'LOADTEST-20260810-%';

SELECT owner, count(*)
FROM fires
WHERE external_card_number LIKE 'LOADTEST-20260810-%'
GROUP BY owner
ORDER BY owner;
