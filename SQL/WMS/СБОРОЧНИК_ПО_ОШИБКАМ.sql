select 
err.ORDER_NUMBER ,
err.CONDITION ,
err.UNIT_COUNT ,
err.UID1 ,
err.EAN ,
pp.nam_mat ,
adr_pic ,
norder ,
uid_ord ,
klient ,
date_sb ,
date_dost 
from RABAEV.ORDER_AUDIT_ERROR_LINES err left join 
(select distinct
       tl.ld_cproin uid_mat,
       ta.ar_libpro nam_mat,
       tlp.lp_adrpic adr_pic,
       te.cd_numorl norder,
       te.cd_numcde uid_ord,
       tlp.lp_nligpr por,
       te.cd_livrea uid_kl,
       te.cd_libliv klient,
       te.cd_vill || ', ' || te.cd_adr1 adr_kl,
       te.cd_datcde date_sb,
       te.cd_datlip date_dost
from
refstock.tb_ecde te
left join refstock.TB_LCDE tl on tl.ld_numorl=te.cd_numorl and tl.ld_donord='RM' and tl.ld_depot='01'  
left join refstock.tb_art ta on ta.ar_cproin=tl.ld_cproin and ta.ar_donord=te.cd_donord 
left join refstock.TB_LPREP tlp on tlp.LP_NUMORL=te.cd_numorl and ta.ar_cproin=tlp.lp_cproin
where 
te.cd_numcde='5422406'
 )  pp  on pp.uid_mat = err.UID1 




where ORDER_NUMBER = '5422406'

order by CONDITION

