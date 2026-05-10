select 
distinct
SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-1 ,1  ) as pic_level,
  UL_CPROIN, 
  UE_ADRUMS , 
  TB_ART.AR_LIBPRO as Èìÿ , 
  TB_ART.AR_PDSUVC  as ÂÁ_ØÒ , -- Âåñ áðóòòî øòóêè
  AR_PDSCAR  as ÂÁ_ÊÎÐ , --    Âåñ áðóòòî êîðîáà
  AR_PDSSPC as ÂÁ_ÁË ,
  AR_PDSPAL as ÂÁ_ÏÀËÅÒÛ , --        Pallet weight in kg base included

 sfera_ean.EAN_SHT , 
 sfera_ean.EAN_BL , 
 sfera_ean.EAN_KOR 
-- TB_ART.*
 from refstock.TB_LCUMS 
left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM'
left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM'
left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID 
where ul_donord='RM'
and not ( sfera_ean.TMC_UID  is null )
and not ( UE_ADRUMS is null)
and  UL_CPROIN= '150659'
and LENGTH(UE_ADRUMS)>=1
and SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-1 ,1  ) in ('1','2')

