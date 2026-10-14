package TRANSPORT_PLN is
  function get_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_time_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function get_dist_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function set_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, time1 number) return int;
  function set_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, dist number) return int;
  function set_time_m(AddrFrom varchar2, AddrTo varchar2, time1 number) return int;
  function set_distance_m(AddrFrom varchar2, AddrTo varchar2, dist1 number) return int;
  function is_tt_just_out_go(tt_id int) return int;
  function upd_tt_perdiction(tt_id int) return int;
  function set_mail_sended(tt_id int) return int;
  function set_tt_closed(tt_id int) return int;
end TRANSPORT_PLN;
