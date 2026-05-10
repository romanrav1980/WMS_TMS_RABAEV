select distinct

/*

ta.AR_N3UVSP    1    штук в блоке
ta.AR_N3SPCA    12    Блоков в коробе


*/
ta.AR_N3UVSP ,
ta.AR_N3SPCA ,

       tlp.LP_USSCCD  , 
       tl.ld_cproin uid_mat,

       LP_UVAPRE kol_sht, 
       ta.ar_libpro nam_mat,
       ta.ar_n3uvsp sht_bl,
       tlp.lp_adrpic adr_pic,
        
       
       ta.ar_n3spca bl_kor,
       trunc(LP_UVAPRE/(ta.ar_n3uvsp*ta.ar_n3spca),0) kor,
       trunc((LP_UVAPRE -(trunc(LP_UVAPRE/(ta.ar_n3uvsp*ta.ar_n3spca),0)*(ta.ar_n3uvsp*ta.ar_n3spca)))/ta.ar_n3uvsp,0) bl,
     


       LP_PTREEL pds_order,
       
       te.cd_numorl norder,

       te.cd_numcde uid_ord,

       tlp.lp_nlotpr lot,

       tlp.lp_nligpr por,

       te.cd_livrea uid_kl,

       te.cd_libliv klient,

       te.cd_vill || ', ' || te.cd_adr1 adr_kl,

       te.cd_datcde date_sb,

       te.cd_datlip date_dost,

       te.cd_quai dock,

       te.cd_ctourn route,

       LP_VTAPRE volume_order

from refstock.tb_ecde te

left join refstock.TB_LCDE tl on tl.ld_numorl=te.cd_numorl and tl.ld_donord='RM' and tl.ld_depot='01'

left join refstock.tb_art ta on ta.ar_cproin=tl.ld_cproin and ta.ar_donord=te.cd_donord 

left join refstock.TB_LPREP tlp on tlp.LP_NUMORL=te.cd_numorl and ta.ar_cproin=tlp.lp_cproin

-- where

-- te.cd_datlip between TRUNC(to_date(:DateFrom,'DD.MM.YY')) and TRUNC(to_date(:DateTo,'DD.MM.YY'))  and 

-- (  te.cd_numcde='5386571' ) -- and

--and (:nRoute is null or :nRoute is not null and  te.cd_ctourn=:nRoute)

--and tlp.LP_UVREEL > 0

-- ld_statut='3'  

order by te.cd_ctourn, te.cd_numcde, tlp.lp_nlotpr, tlp.lp_nligpr



