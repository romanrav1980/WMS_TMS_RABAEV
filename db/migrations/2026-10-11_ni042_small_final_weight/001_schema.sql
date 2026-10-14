alter table RRL_PALLET_TYPE add(FINAL_WEIGHT_REQUIRED number(1)default 0 not null constraint RRL_PT_FINAL_WEIGHT_CK check(FINAL_WEIGHT_REQUIRED in(0,1)));
