const params = new URLSearchParams(window.location.search);
const orderId = params.get("order_id");

let currentOrder = null;
let currentInvoice = null;

function getInvoiceElement() {
  return document.getElementById("invoice") || document.getElementById("invoice-container");
}

async function loadInvoice() {
  const container = getInvoiceElement();
  if (!orderId) {
    if (container) {
      container.innerHTML = `<div class="error-msg">No Order ID found</div>`;
    }
    return;
  }

  try {
    await CONFIG.loadCafeConfig();
    const res = await fetch(`${CONFIG.API_URL}/api/orders/${orderId}`);
    if (!res.ok) throw new Error("Order not found");
    currentOrder = await res.json();
    
    // If order is paid, retrieve the corresponding invoice record
    if (currentOrder.status === "PAID") {
      try {
        const invRes = await fetch(`${CONFIG.API_URL}/api/invoices/order/${orderId}`);
        if (invRes.ok) {
          currentInvoice = await invRes.json();
        }
      } catch (invErr) {
        console.error("Failed to load invoice record:", invErr);
      }
    }
    
    renderInvoice();
  } catch (err) {
    console.error("Invoice load failed:", err);
    if (container) {
      container.innerHTML = `
        <div class="error-msg">Order not found</div>
        <button class="pay-btn" style="margin-top: 16px;" onclick="loadInvoice()">Try Again</button>
      `;
    }
  }
}

function renderInvoice() {
  if (!currentOrder) return;
  
  let total = 0;
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  let itemsHtml = "";
  const items = currentOrder.items || [];
  const currencySymbol = CONFIG.cafe ? CONFIG.cafe.currency_symbol : '₹';
  items.forEach(i => {
    const price = Number(i.price) || 0;
    const qty = Number(i.qty) || 0;
    const subtotal = price * qty;
    total += subtotal;
    itemsHtml += `
      <div class="receipt-row">
        <span class="col-item">${i.name || 'Unknown Item'}</span>
        <span class="col-qty">${qty}</span>
        <span class="col-price">${currencySymbol}${price.toFixed(2)}</span>
        <span class="col-amt">${currencySymbol}${subtotal.toFixed(2)}</span>
      </div>
    `;
  });

  const gstPercentage = CONFIG.cafe ? CONFIG.cafe.gst_percentage : 5.0;
  const taxFactor = 1 + (gstPercentage / 100);
  const subtotalVal = total / taxFactor;
  const gstTotal = total - subtotalVal;
  const cgstVal = gstTotal / 2;
  const sgstVal = gstTotal / 2;

  const orderStatus = currentOrder.status || 'OPEN';
  const tableId = currentOrder.table_id || 'N/A';
  const orderIdVal = currentOrder.order_id || '';
  const displayOrderId = orderIdVal ? orderIdVal.substring(0, 8).toUpperCase() : 'N/A';

  const paidHtml = orderStatus === "PAID"
    ? `<div class="paid-badge-capsule">
        <div class="paid-title">PAID</div>
        <div class="paid-detail">MODE: ${currentInvoice ? (currentInvoice.payment_method || 'CASH') : 'CASH'}</div>
        <div class="paid-detail">DATE: ${dateStr} @ ${timeStr}</div>
       </div>`
    : "";

  const actionHtml = orderStatus === "PAID"
    ? `<div class="action-container" style="margin-top: 20px;">
        <button class="pay-btn print-btn" onclick="printAndClose()">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
          Print Invoice
        </button>
       </div>`
    : `
      <div class="action-container" style="margin-top: 20px; display: flex; flex-direction: column; gap: 12px;">
        <div style="text-align: left; width: 100%;">
          <label style="font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; display: block; margin-bottom: 8px;">Select Payment Mode</label>
          <select id="invoicePayMethod" class="pay-select">
            <option value="CASH">Cash</option>
            <option value="UPI">UPI / QR Code</option>
          </select>
        </div>
        <button class="pay-btn" id="payBtn" onclick="payWithSelectedMode()">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Process Payment
        </button>
      </div>
    `;

  const container = getInvoiceElement();
  if (container) {
    const cafeName = CONFIG.cafe ? CONFIG.cafe.cafe_name : 'Aero Cafe';
    const cafeAddress = CONFIG.cafe ? CONFIG.cafe.cafe_address : '';
    const cafePhone = CONFIG.cafe ? CONFIG.cafe.cafe_phone : '';
    const cafeGstin = CONFIG.cafe ? CONFIG.cafe.cafe_gstin : '';
    
    let headerDetailHtml = "";
    if (cafeAddress) headerDetailHtml += `<div class="inv-address-line">${cafeAddress}</div>`;
    if (cafePhone) headerDetailHtml += `<div class="inv-address-line">Phone: ${cafePhone}</div>`;
    if (cafeGstin) headerDetailHtml += `<div class="inv-address-line">GSTIN: ${cafeGstin}</div>`;

    container.innerHTML = `
      <div class="inv-header">
        <img
          class="inv-logo"
          src="../assets/images/caffe.png"
          alt="${cafeName}"
          id="invLogo"
        />
        <div class="inv-name">${cafeName}</div>
        ${headerDetailHtml}
      </div>

      <div class="inv-divider"></div>

      <div class="meta-grid">
        <div class="meta-item"><span>TABLE:</span> <strong>${tableId}</strong></div>
        <div class="meta-item"><span>DATE:</span> <span>${dateStr}</span></div>
        <div class="meta-item"><span>TIME:</span> <span>${timeStr}</span></div>
        <div class="meta-item"><span>ORDER:</span> <span>#${displayOrderId}</span></div>
        ${currentInvoice ? `<div class="meta-item" style="grid-column: span 2"><span>INVOICE:</span> <strong>#INV-${currentInvoice.invoice_id || ''}</strong></div>` : ''}
      </div>

      <div class="inv-divider"></div>

      <div class="inv-section-title">Billing Items</div>
      <div class="receipt-row header">
        <span class="col-item">ITEM DESCRIPTION</span>
        <span class="col-qty">QTY</span>
        <span class="col-price">PRICE</span>
        <span class="col-amt">AMOUNT</span>
      </div>
      ${itemsHtml}

      <div class="inv-divider"></div>

      <div class="calc-row">
        <span>Subtotal (Excl. Tax)</span>
        <span>${currencySymbol}${subtotalVal.toFixed(2)}</span>
      </div>
      <div class="calc-row">
        <span>CGST (${(gstPercentage/2).toFixed(1)}%)</span>
        <span>${currencySymbol}${cgstVal.toFixed(2)}</span>
      </div>
      <div class="calc-row">
        <span>SGST (${(gstPercentage/2).toFixed(1)}%)</span>
        <span>${currencySymbol}${sgstVal.toFixed(2)}</span>
      </div>
      <div class="inv-divider-double"></div>
      <div class="calc-row grand-total">
        <span>GRAND TOTAL</span>
        <span>${currencySymbol}${total.toFixed(2)}</span>
      </div>

      <div class="inv-divider"></div>

      <div class="inv-footer">
        Please visit again!
      </div>

      ${paidHtml}
      ${actionHtml}
    `;
  }
}

async function payWithSelectedMode() {
  if (!currentOrder) return;

  const payBtn = document.getElementById("payBtn");
  const method = document.getElementById("invoicePayMethod").value;
  payBtn.disabled = true;
  payBtn.innerHTML = "Processing...";

  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${CONFIG.API_URL}/api/invoices`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ order_id: currentOrder.order_id, payment_method: method })
    });

    if (res.ok) {
      currentOrder.status = "PAID";
      currentInvoice = await res.json();
      renderInvoice();
      setTimeout(() => { window.close(); }, 1500);
    } else {
      alert("Payment confirmation failed! Please try again.");
      payBtn.disabled = false;
      payBtn.innerHTML = "Process Payment";
    }
  } catch (err) {
    console.error("Payment error:", err);
    alert("Server connection error!");
    payBtn.disabled = false;
    payBtn.innerHTML = "Process Payment";
  }
}

function printAndClose() {
  window.print();
  setTimeout(() => { window.close(); }, 500);
}

loadInvoice();
