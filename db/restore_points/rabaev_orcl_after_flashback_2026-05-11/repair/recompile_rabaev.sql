prompt Recompile RABAEV schema after flashback repair
begin
  dbms_utility.compile_schema(schema => 'RABAEV', compile_all => false);
end;
/
