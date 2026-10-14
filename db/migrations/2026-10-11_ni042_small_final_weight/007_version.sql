alter table RRL_PALLET_TYPE add(TYPE_VERSION number(10)default 1 not null constraint RRL_PT_VERSION_CK check(TYPE_VERSION>=1));
