select BASE_UOM,count(distinct ARTICUL) ARTICLES,count(*) CONVERSIONS from RRL_STOCK_UOM_CONVERSION group by BASE_UOM;
select count(*) MOJIBAKE from RRL_STOCK_UOM_CONVERSION where instr(INPUT_UOM,unistr('\0420\00A0'))>0;
