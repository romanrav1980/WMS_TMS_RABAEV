/* Formatted on 13.12.2009 12:52:18 (QP5 v5.115.810.9015) */
SELECT SUBSTR (ue_adrums, LENGTH (ue_adrums), 1) AS секци€,
       SUBSTR (ue_adrums, LENGTH (ue_adrums) - 2, 2) AS этаж,
       SUBSTR (ue_adrums, LENGTH (ue_adrums) - 5, 3) AS раздел,
       SUBSTR (ue_adrums, LENGTH (ue_adrums) - 7, 2) AS стеллаж,
       SUM (ul_nqtuvc)  ќЋ»„,
       TRUNC (SUM (ul_nqtuvc) / (tb_art.ar_n3uvsp * tb_art.ar_n3spca), 0) kor,
       TRUNC ( (SUM (ul_nqtuvc)
                - (TRUNC (SUM (ul_nqtuvc)
                          / (tb_art.ar_n3uvsp * tb_art.ar_n3spca),
                          0
                   )
                   * (tb_art.ar_n3uvsp * tb_art.ar_n3spca)))
              / tb_art.ar_n3uvsp,
              0
       )
          bl,
       ul_cproin,
       ar_libpro,
       ue_adrums,
       MAX (TO_DATE (ut_valind, 'YYYY.MM.DD')) Ћучший—рок,
       MIN (TO_DATE (ut_valind, 'YYYY.MM.DD')) ’удший—рок
FROM                refstock.tb_lcums
                 LEFT JOIN
                    refstock.tb_eums
                 ON ue_usscc = ul_usscc AND ue_depot = 01 AND ue_propri = 'RM'
              LEFT JOIN
                 refstock.tb_art
              ON ar_cproin = ul_cproin AND ar_donord = 'RM'
           LEFT JOIN
              refstock.tb_traums
           ON ue_usscc = ut_usscc AND ul_numlig = ut_numlig
        LEFT JOIN
           refstock.tb_rack
        ON     rk_depot = '01'
           AND ue_zone = rk_zone
           AND ue_allee = rk_allee
           AND ue_travee = rk_travee
           AND rk_niveau = ue_niveau
     LEFT JOIN
        rabaev.sfera_ean sfera_ean
     ON ul_cproin = sfera_ean.tmc_uid
WHERE     ul_donord = 'RM'
      AND (ul_numorl IS NULL)
      AND ul_nqtuvc <> 0
     AND SUBSTR (ue_adrums, LENGTH(ue_adrums) - 5, 3) = '002'
      AND SUBSTR (ue_adrums, LENGTH (ue_adrums) - 7, 2) = '01'
GROUP BY ul_cproin,
         ar_libpro,
         ar_nrsfou,
         ue_adrums,
         tb_art.ar_n3uvsp,
         tb_art.ar_n3spca
ORDER BY SUBSTR (ue_adrums, LENGTH (ue_adrums) - 7, 2),
         SUBSTR (ue_adrums, LENGTH (ue_adrums) - 5, 3),
         SUBSTR (ue_adrums, LENGTH (ue_adrums) - 2, 2),
         SUBSTR (ue_adrums, LENGTH (ue_adrums), 1)