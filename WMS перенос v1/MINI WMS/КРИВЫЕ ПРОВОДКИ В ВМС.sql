

select rs.*  from rrl_sborka_pallet_rows rs, rrl_sborka_pallets pts
where rs.pallet_uid=pts.pallet_uid and pts.condition=2 and rs.id_event is null
and pts.create_date >=  TO_DATE( '17.10.2011 13:19:57' , 'dd.mm.YYYY HH24:MI:SS' )  
and rs.quantity>0
