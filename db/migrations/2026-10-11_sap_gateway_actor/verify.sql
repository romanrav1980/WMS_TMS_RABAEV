select ID,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN,
RRL_HAS_WRIGHT(ID,'sap_article_import')MASTER_IMPORT,
RRL_HAS_WRIGHT(ID,'sap_store_order_import')ORDER_IMPORT,
RRL_HAS_WRIGHT(ID,'sap_store_all_ware')SOURCE_WIDE,
RRL_HAS_WRIGHT(ID,'warehouse_receipt_confirm')RECEIPT_WRITE,
RRL_HAS_WRIGHT(ID,'wms_admin_login')SHELL_LOGIN
from RUSERS where ID='SAP_FILE_GATEWAY';
select object_name,object_type,status from user_objects where object_name='RRL_STORE_ORDER_SCOPE';
