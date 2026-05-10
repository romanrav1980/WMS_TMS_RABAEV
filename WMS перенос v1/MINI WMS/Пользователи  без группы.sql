select U.* from RUSERS U , RIGHTS R 
where U.USER_GROUP=R.USER_GROUP(+)
and  ( R.USER_GROUP is null )