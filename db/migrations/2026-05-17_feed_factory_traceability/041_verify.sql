-- Migration 041 — Verify
-- Проверяет, что все объекты созданы корректно.

SELECT 'AISLE_LABEL' col_name,
       CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END status
  FROM user_tab_columns
 WHERE table_name = 'RRL_TOPOLOGY_AISLE'
   AND column_name = 'AISLE_LABEL'
UNION ALL
SELECT 'DISTANCE_FROM_START_M',
       CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END
  FROM user_tab_columns
 WHERE table_name = 'RRL_TOPOLOGY_AISLE'
   AND column_name = 'DISTANCE_FROM_START_M'
UNION ALL
SELECT 'AISLE_WIDTH_M',
       CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END
  FROM user_tab_columns
 WHERE table_name = 'RRL_TOPOLOGY_AISLE'
   AND column_name = 'AISLE_WIDTH_M'
UNION ALL
SELECT 'RRL_TOPOLOGY_PICK_FACE_SLOT',
       CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END
  FROM user_tables
 WHERE table_name = 'RRL_TOPOLOGY_PICK_FACE_SLOT'
UNION ALL
SELECT 'RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ',
       CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END
  FROM user_sequences
 WHERE sequence_name = 'RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ';
