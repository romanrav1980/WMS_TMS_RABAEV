select distinct 
 tlp.LP_USSCCD  ,  
  tl.ld_cproin uid_mat,  
  LP_UVAPRE kol_sht,  
   ta.ar_libpro nam_mat,  
   tlp.lp_adrpic adr_pic,  
   ta.ar_n3uvsp sht_bl  ,
    te.cd_ctourn, te.cd_numcde, tlp.lp_nlotpr, tlp.lp_nligpr
   from refstock.tb_ecde te  
   left join refstock.TB_LCDE tl on tl.ld_numorl=te.cd_numorl and tl.ld_donord='RM' and tl.ld_depot='01'  
   left join refstock.tb_art ta on ta.ar_cproin=tl.ld_cproin and ta.ar_donord=te.cd_donord   
   left join refstock.TB_LPREP tlp on tlp.LP_NUMORL=te.cd_numorl and ta.ar_cproin=tlp.lp_cproin  
   
   left join RABAEV.SFERA_EAN sfera_ean on  tl.ld_cproin=sfera_ean.TMC_UID
   
--   where (    tlp.LP_USSCCD ='036376530005389040' )   
   
   
 order by te.cd_ctourn, te.cd_numcde, tlp.lp_nlotpr, tlp.lp_nligpr


