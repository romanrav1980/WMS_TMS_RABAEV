-- Rare metadata/placement changes take CONFIG X before any document or slot lock.
-- This grants no stock/configuration write context and cannot conduct quantities.
create or replace package RRL_STOCK_METADATA_TX authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/
