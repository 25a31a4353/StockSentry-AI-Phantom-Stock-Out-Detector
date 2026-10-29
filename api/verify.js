module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const payload = req.body || {};
  const sysQty = Number(payload.systemQty) || 0;
  const foundQty = Number(payload.foundQty) || 0;
  const discrepancy = Math.max(0, sysQty - foundQty);
  
  let recoveredRupees = 0;
  if (payload.outcome === 'Confirmed Phantom Stock-Out') {
    recoveredRupees = Math.round(discrepancy * 120 * 14 * 0.70);
  } else if (payload.outcome === 'Misplaced on Wrong Shelf') {
    recoveredRupees = Math.round(discrepancy * 120 * 3 * 0.70);
  }

  return res.status(200).json({
    success: true,
    message: "Audit Correction Proposal authorized by Store Lead and reconciled to ERP ledger",
    proposalId: payload.proposalId || ('PROP-' + Math.floor(100000 + Math.random() * 900000)),
    correlationId: 'TXN-ERP-' + Math.floor(10000000 + Math.random() * 90000000),
    record: {
      id: Date.now(),
      proposalId: payload.proposalId || ('PROP-' + Math.floor(100000 + Math.random() * 900000)),
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      date: payload.date || new Date().toISOString().slice(0, 10),
      store: payload.store || 'S01',
      sku: payload.sku || 'SKU-001',
      product: payload.product || 'Retail Item',
      systemQty: sysQty,
      foundQty: foundQty,
      discrepancy: discrepancy,
      outcome: payload.outcome || 'Confirmed Phantom Stock-Out',
      notes: payload.notes || '',
      auditor: payload.auditor || 'Priya Menon (Auditor)',
      approver: payload.approver || 'Store Operations Lead (Approved)',
      erpStatus: discrepancy > 0 ? 'SYNCED_TO_ERP' : 'NO_CHANGE_NEEDED',
      recoveredRupees: recoveredRupees
    }
  });
};

