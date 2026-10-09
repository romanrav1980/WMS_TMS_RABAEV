"""Emit bounded UI/API edits as UTF-8 file contents for the native writer."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = {}
def replace(path, old, new):
    text = files.get(path, (ROOT / path).read_text(encoding="utf-8"))
    if text.count(old) != 1:
        raise RuntimeError("Expected one anchor: " + path + " " + old[:60])
    files[path] = text.replace(old, new, 1)

replace("api/wms_api_server/app/modules/integrations/application/receipt_ports.py",
    "    def get(self, order_id: str) -> dict: ...",
    "    def get(self, order_id: str) -> dict: ...\n    def by_receipt_document(self, document_id: int) -> dict: ...")
replace("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py",
    "    def get(self, order_id: str) -> dict:",
    """    def by_receipt_document(self, document_id: int) -> dict:
        rows = self.gateway.fetch_all(
            "select ORDER_ID from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=:i",
            {"i": document_id})
        if not rows:
            raise LookupError("Накладная не связана с разрешённой поставкой SAP")
        if len(rows) != 1:
            raise ValueError("Неоднозначная связь накладной с заказом SAP")
        return self.get(rows[0]["order_id"])

    def get(self, order_id: str) -> dict:""")
replace("api/wms_api_server/app/modules/integrations/api/supply_routes.py",
    '@router.get("/{order_id}")',
    """@router.get("/by-receipt-document/{document_id}")
def supply_by_document(document_id: int,
                       user: AdminUser = Depends(require_permission("sap_supply_view")),
                       service: SupplyOrders = Depends(supply_service)) -> dict:
    if document_id < 1:
        raise HTTPException(422, "Положительный номер накладной обязателен")
    try:
        return service.by_receipt_document(document_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/{order_id}")""")
replace("wiki-raw/wms_admin_ui_reference/receiving.js",
    "  async function loadOrders() {",
    """  const sourceDocument = new URLSearchParams(location.search).get('receipt_document_id');
  let sourceOpened = false;
  async function loadOrders() {""")
replace("wiki-raw/wms_admin_ui_reference/receiving.js",
    "      message(orders.length?'Выберите заказ SAP.':'Заказов SAP нет. Ожидается файл от шлюза.');",
    """      message(orders.length?'Выберите заказ SAP.':'Заказов SAP нет. Ожидается файл от шлюза.');
      if(sourceDocument && !sourceOpened){
        if(!/^[1-9][0-9]*$/.test(sourceDocument))throw new Error('Некорректный номер накладной.');
        const selected=await api('/api/integrations/sap/supply-orders/by-receipt-document/'+encodeURIComponent(sourceDocument));
        sourceOpened=true;await selectOrder(selected.order_id);
        message('Открыта поставка выбранной накладной. Приёмка — по паллетам и сканированию; размещение — через задания.');
      }""")
# Auth can fire before this script subscribes; support both initialized and later login.
replace("wiki-raw/wms_admin_ui_reference/receiving.js",
    "  el('receiptRefresh').addEventListener('click',loadOrders);",
    """  window.addEventListener('wms-admin-auth-ready',loadOrders);
  if(window.wmsAdminAuth.state.user)loadOrders();
  el('receiptRefresh').addEventListener('click',loadOrders);""")
path = "WindowsApplication2/WindowsApplication2/Form1.cs"
helper = """        // The modern workflow requires SAP authorization and pallet scan facts.
        // No tokens or credentials are transferred to the browser.
        private bool OpenExplicitReceiptWorkflow()
        {
            string state = obj2str(CachedQuerySingle(
                "select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")).Trim();
            if (state == "PREPARED") return false;
            if (state != "ACTIVE")
                throw new InvalidOperationException("Проводки временно остановлены: " + state);
            if (dataGridView_prihod.CurrentRow == null)
                throw new InvalidOperationException("Выберите накладную.");
            int document = Convert.ToInt32(dataGridView_prihod.CurrentRow.Cells[6].Value);
            string configured = Environment.GetEnvironmentVariable("WMS_RECEIVING_URL");
            Uri address;
            if (!Uri.TryCreate(String.IsNullOrEmpty(configured) ?
                    "http://127.0.0.1:3000/receiving.html" : configured, UriKind.Absolute, out address)
                || (address.Scheme != Uri.UriSchemeHttp && address.Scheme != Uri.UriSchemeHttps))
                throw new InvalidOperationException("Неверный WMS_RECEIVING_URL.");
            UriBuilder target = new UriBuilder(address);
            target.Query = (String.IsNullOrEmpty(address.Query) ? "" : address.Query.Substring(1) + "&")
                + "receipt_document_id=" + document.ToString(System.Globalization.CultureInfo.InvariantCulture);
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(target.Uri.AbsoluteUri)
                { UseShellExecute = true });
            return true;
        }

"""
replace(path,"        private void Закрыть_Click(object sender, EventArgs e)",
    helper+"        private void Закрыть_Click(object sender, EventArgs e)")
# Short circuit before optimistic grid or Oracle DML; PREPARED retains old behavior.
replace(path,"""        private void Закрыть_Click(object sender, EventArgs e)
        {  ""","""        private void Закрыть_Click(object sender, EventArgs e)
        {
            try { if (OpenExplicitReceiptWorkflow()) return; }
            catch (Exception ex) { MessageBox.Show(ex.Message); return; }
            """)
replace(path,"""        private void Откатить_Click(object sender, EventArgs e)
        {
""","""        private void Откатить_Click(object sender, EventArgs e)
        {
            try
            {
                if (OpenExplicitReceiptWorkflow())
                {
                    MessageBox.Show("Удаление движений отменено. Для принятого товара используйте сторно с причиной; для размещения — отмену задания.");
                    return;
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); return; }
""")
replace(path,"""        private void Разместить_Click(object sender, EventArgs e)
        {
            try
            {""","""        private void Разместить_Click(object sender, EventArgs e)
        {
            try
            {
                if (OpenExplicitReceiptWorkflow()) return;""")
print(json.dumps(files,ensure_ascii=True))
