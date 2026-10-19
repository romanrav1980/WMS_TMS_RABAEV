create or replace package RRL_STOCK_WAVE_READY authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure assert_released(p_wave number);
end;

/
