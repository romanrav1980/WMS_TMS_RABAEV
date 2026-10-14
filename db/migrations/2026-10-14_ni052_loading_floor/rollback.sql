begin
 raise_application_error(-20863,'Forward-only: removing physical floor guard requires retained facts/currentscope recovery; do not restore unprotected load/depart bodies');
end;
/
