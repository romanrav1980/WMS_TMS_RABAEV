set define off
SELECT object_name, object_type FROM user_objects WHERE status='INVALID' AND object_name NOT LIKE 'BIN$%' ORDER BY object_type, object_name;
SELECT name, type, line, text FROM user_errors WHERE attribute='ERROR' AND name NOT LIKE 'BIN$%' ORDER BY name, sequence;
