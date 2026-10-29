const INITIAL_AUDITS = [
  {
    id: 6,
    timestamp: "2026-10-27 09:55:00",
    date: "2026-10-27",
    store: "S04",
    sku: "SKU-578",
    product: "Cold Coffee 250ml",
    systemQty: 18,
    foundQty: 0,
    discrepancy: 18,
    outcome: "Confirmed Phantom Stock-Out",
    notes: "Cooler display empty. 18 units missing from shrinkage.",
    auditor: "Vikram Patel",
    erpStatus: "SYNCED_TO_ERP",
    recoveredRupees: 8200.0
  },
  {
    id: 5,
    timestamp: "2026-10-27 09:20:00",
    date: "2026-10-27",
    store: "S01",
    sku: "SKU-412",
    product: "Shampoo 340ml",
    systemQty: 11,
    foundQty: 11,
    discrepancy: 0,
    outcome: "Stock Actually Present",
    notes: "Verified on top shelf. False positive due to category promotion ending.",
    auditor: "Priya Menon",
    erpStatus: "NO_CHANGE_NEEDED",
    recoveredRupees: 0.0
  },
  {
    id: 4,
    timestamp: "2026-10-26 10:10:00",
    date: "2026-10-26",
    store: "S03",
    sku: "SKU-319",
    product: "Laundry Pods 30pk",
    systemQty: 22,
    foundQty: 0,
    discrepancy: 22,
    outcome: "Confirmed Phantom Stock-Out",
    notes: "Confirmed warehouse short-shipment. ERP corrected.",
    auditor: "Rajesh Sharma",
    erpStatus: "SYNCED_TO_ERP",
    recoveredRupees: 12400.0
  },
  {
    id: 3,
    timestamp: "2026-10-26 08:45:00",
    date: "2026-10-26",
    store: "S02",
    sku: "SKU-087",
    product: "Instant Noodles 280g",
    systemQty: 7,
    foundQty: 0,
    discrepancy: 7,
    outcome: "Confirmed Phantom Stock-Out",
    notes: "Zero shelf facings. Unrecorded damaged batch.",
    auditor: "Sunita Rao",
    erpStatus: "SYNCED_TO_ERP",
    recoveredRupees: 3150.0
  },
  {
    id: 2,
    timestamp: "2026-10-25 09:32:00",
    date: "2026-10-25",
    store: "S01",
    sku: "SKU-221",
    product: "Protein Bar 60g",
    systemQty: 14,
    foundQty: 2,
    discrepancy: 12,
    outcome: "Misplaced on Wrong Shelf",
    notes: "Found 2 units behind cereal boxes in aisle 3. Restocked.",
    auditor: "Priya Menon",
    erpStatus: "SYNCED_TO_ERP",
    recoveredRupees: 1850.0
  },
  {
    id: 1,
    timestamp: "2026-10-25 09:15:00",
    date: "2026-10-25",
    store: "S01",
    sku: "SKU-104",
    product: "Sparkling Water 500ml",
    systemQty: 9,
    foundQty: 0,
    discrepancy: 9,
    outcome: "Confirmed Phantom Stock-Out",
    notes: "Shelf completely bare. Writing off 9 units and triggering PO.",
    auditor: "Priya Menon",
    erpStatus: "SYNCED_TO_ERP",
    recoveredRupees: 4250.0
  }
];

module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.status(200).json(INITIAL_AUDITS);
};

