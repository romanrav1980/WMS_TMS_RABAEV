alter table RRL_WH_FINAL_SCALE_USE add SIGNATURE_VERSION number(2)default 2 not null;
alter table RRL_WH_FINAL_SCALE_USE add constraint RRL_WH_FINAL_USE_VERSION_C check(SIGNATURE_VERSION in(2,3));
