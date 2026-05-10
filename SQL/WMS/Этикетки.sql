select 
  ue_adrres,
  ue_usscc,
  ul_cproin,
  ul_arprom,
  ul_ilogis,
  ar_libpro,
  UL_NUVSPC,
  UL_NSPCCA,
  UL_NCACOU,
  UL_NCOUPA,
  ul_donord,
  UE_PDSUMS,
  ceil(UL_NQTUVC/UL_NUVSPC/UL_NSPCCA) UL_NQTUVC,
  to_date(UL_DATCRE,'DD.MM.YY') OE_DATREC,
  to_date(UT_VALIND,'YYYY.MM.DD') UT_VALIND
from TB_LCUMS,  tb_eums, tb_art, TB_TRAUMS
where 

 (&DateFrom is null and &DateTo is null or
 &DateFrom is null and &DateTo is not null and to_char(UL_DATCRE,'dd.mm.yy') = to_char(to_date(&DateTo,'DD.MM.YY'),'dd.mm.yy') or
 &DateFrom is not null and &DateTo is null and to_char(UL_DATCRE,'dd.mm.yy') = to_char(to_date(&DateFrom,'DD.MM.YY'),'dd.mm.yy') or
 &DateFrom is not null and &DateTo is not null and to_char(UL_DATCRE,'dd.mm.yy') between to_char(to_date(&DateFrom,'DD.MM.YY'),'dd.mm.yy') and to_char(to_date(&DateTo,'DD.MM.YY'),'dd.mm.yy'))

and ul_donord = 'RM'
and ue_usscc = ul_usscc and ue_depot = 01
and ar_cproin = ul_cproin and ar_donord = 'RM' 
and ut_usscc = ue_usscc

--and OE_NUMORC = &nOrder--'12485' םמלונ ÒÏÍ

and (&nOrder is null or &nOrder is not null and UL_NUMORC  like &nOrder)
and (&nUSSCC is null or &nUSSCC is not null and ue_usscc like &nUSSCC)
and (&nUID is null or &nUID is not null and ul_cproin like &nUID)
and (&nADR is null or &nADR is not null and ue_adrres like &nADR)
