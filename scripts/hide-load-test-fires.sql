\set ON_ERROR_STOP on

UPDATE fires
SET deleted_at = COALESCE(deleted_at, now())
WHERE external_card_number LIKE 'LOADTEST-20260810-%'
  AND substring(external_card_number FROM '([0-9]+)$')::integer > 1000;

SELECT
  count(*) FILTER (WHERE deleted_at IS NULL) AS visible_load_test_fires,
  count(*) FILTER (WHERE deleted_at IS NOT NULL) AS hidden_load_test_fires
FROM fires
WHERE external_card_number LIKE 'LOADTEST-20260810-%';
