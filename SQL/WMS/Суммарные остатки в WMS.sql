select 
  UL_CPROIN УИД ,
  sum(UL_NQTUVC) КОЛИЧЕСТВО ,
  AR_LIBPRO  НАИМЕНОВАНИЕ
from refstock.TB_LCUMS 
left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM'
left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM'
left join refstock.tb_traums on ue_usscc=ut_usscc and ul_numlig=ut_numlig
left join refstock.TB_RACK on rk_depot='01' and ue_zone=rk_zone and ue_allee=rk_allee and ue_travee=rk_travee and rk_niveau=ue_niveau
left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID
where ul_donord='RM'
and ul_numorl is null  -- не показывать то что уже в заказах
and ul_nqtuvc<>0
group by   UL_CPROIN ,  AR_LIBPRO


