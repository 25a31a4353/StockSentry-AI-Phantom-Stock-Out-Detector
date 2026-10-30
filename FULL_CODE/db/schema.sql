-- StockSentry AI — Database Schema & Initial Seed
-- Architecture: SQLite 3 ACID Operational Ground-Truth Store

CREATE TABLE IF NOT EXISTS audit_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    date_recorded TEXT NOT NULL,
    store_id TEXT NOT NULL,
    sku_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    system_qty INTEGER NOT NULL,
    physical_qty INTEGER NOT NULL,
    discrepancy INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    notes TEXT,
    auditor TEXT NOT NULL,
    erp_status TEXT NOT NULL DEFAULT 'SYNCED_TO_ERP',
    recovered_rupees REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS erp_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id TEXT NOT NULL,
    sku_id TEXT NOT NULL,
    product_name TEXT,
    category TEXT,
    price REAL,
    on_hand_qty INTEGER NOT NULL,
    expected_demand REAL,
    last_sync TEXT,
    last_reconciled TEXT,
    adjustment_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_audit_store_date ON audit_verifications(store_id, date_recorded);
CREATE INDEX IF NOT EXISTS idx_audit_sku ON audit_verifications(sku_id);
CREATE INDEX IF NOT EXISTS idx_erp_store_sku ON erp_ledger(store_id, sku_id);

-- Controlled Operational Seed (Demo Ground Truth)
INSERT INTO audit_verifications (timestamp, date_recorded, store_id, sku_id, product_name, system_qty, physical_qty, discrepancy, outcome, notes, auditor, erp_status, recovered_rupees)
VALUES
    ('2026-10-30T09:15:00Z', '2026-10-30', 'S01', 'SKU-001', 'Premium Basmati Rice 5kg', 14, 0, -14, 'Confirmed Phantom Stock-Out', 'Shelf physically empty; zero on gondola. Reconciled inventory.', 'Priya Menon', 'SYNCED_TO_ERP', 11480.0),
    ('2026-10-30T09:42:00Z', '2026-10-30', 'S01', 'SKU-003', 'Organic Cold Pressed Mustard Oil 1L', 8, 2, -6, 'Misplaced Inventory Found', 'Recovered 2 units behind Aisle 4 cleaning section.', 'Priya Menon', 'SYNCED_TO_ERP', 4800.0),
    ('2026-10-30T10:05:00Z', '2026-10-30', 'S01', 'SKU-005', 'High-Protein Almond Drink 200ml', 22, 0, -22, 'Confirmed Phantom Stock-Out', 'System indicated 22 units on hand; backroom and shelf empty. Zero sales for 11 days.', 'Priya Menon', 'SYNCED_TO_ERP', 8520.0);

