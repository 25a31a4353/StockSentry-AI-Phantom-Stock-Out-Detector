/**
 * StockSentry AI — Master Data Catalog & Multi-Store Operational Generator
 * 
 * Provides:
 * - 25 Store Masters (City, Tier, Format, Size, Manager)
 * - 800 SKU Master Catalog (Category, Price, Margin, Velocity)
 * - Calibrated Multi-Anomaly Operational Dataset
 *   Every store features a smoothly distributed, realistic Top-20 queue
 *   with varied scores (96 down to 53), diverse confidence levels (98% down to 55%),
 *   distinct zero-sales streaks, and distinct plain-English root causes.
 */

window.StockSentryData = (() => {
  'use strict';

  // 1. Store Master (25 Stores across India)
  const cities = [
    { name: 'Hyderabad', tier: 'Tier 1' },
    { name: 'Bengaluru', tier: 'Tier 1' },
    { name: 'Mumbai', tier: 'Tier 1' },
    { name: 'Chennai', tier: 'Tier 1' },
    { name: 'Kolkata', tier: 'Tier 1' },
    { name: 'Pune', tier: 'Tier 1' },
    { name: 'Vijayawada', tier: 'Tier 2' },
    { name: 'Visakhapatnam', tier: 'Tier 2' },
    { name: 'Guntur', tier: 'Tier 2' },
    { name: 'Kochi', tier: 'Tier 2' },
    { name: 'Coimbatore', tier: 'Tier 2' },
    { name: 'Nagpur', tier: 'Tier 2' },
    { name: 'Indore', tier: 'Tier 2' },
    { name: 'Bhopal', tier: 'Tier 2' },
    { name: 'Vadodara', tier: 'Tier 2' }
  ];

  const formats = ['Supermarket', 'Hypermarket', 'Express Store', 'Daily Mart'];
  const managers = [
    'Priya Menon', 'Rajesh Sharma', 'Arun Kumar', 'Sunita Rao', 'Vikram Patel',
    'Ananya Sen', 'Karthik Iyer', 'Meera Nair', 'Sanjay Verma', 'Deepa Joshi',
    'Manoj Tiwari', 'Pooja Reddy', 'Amitabh Das', 'Kavita Pillai', 'Rohan Gupta'
  ];

  const stores = Array.from({ length: 25 }, (_, i) => {
    const idNum = i + 1;
    const storeId = `S${String(idNum).padStart(2, '0')}`;
    const cityInfo = cities[i % cities.length];
    const format = formats[i % formats.length];
    const tier = cityInfo.tier;
    const size = format === 'Hypermarket' ? 'Large (45k sq.ft)' : format === 'Supermarket' ? 'Medium (18k sq.ft)' : 'Compact (6k sq.ft)';
    const manager = managers[i % managers.length];

    return {
      id: storeId,
      name: `Store ${storeId} — ${cityInfo.name} ${format}`,
      city: cityInfo.name,
      tier,
      format,
      size,
      manager,
      skuCount: 800,
      complianceRate: 85 + (i % 14)
    };
  });

  // 2. SKU Master Catalog (800 SKUs across 8 categories)
  const categories = [
    'Beverages', 'Snacks', 'Grocery & Staples', 'Personal Care',
    'Home Care', 'Dairy & Fresh', 'Packaged Food', 'Household Essentials'
  ];

  const productTemplates = {
    'Beverages': ['Sparkling Water 500ml', 'Cold Brew Coffee 250ml', 'Almond Milk 1L', 'Green Tea Infusion 25 bags', 'Mango Nectar 1L', 'Zero Sugar Cola 330ml', 'Coconut Water 200ml', 'Energy Drink 250ml'],
    'Snacks': ['Roasted Almonds 200g', 'Masala Potato Crisps 120g', 'Protein Bar 60g', 'Multigrain Crackers 150g', 'Salted Cashews 200g', 'Corn Nachos 150g', 'Dark Chocolate 80g', 'Peanut Butter Wafers 100g'],
    'Grocery & Staples': ['Basmati Rice 5kg', 'Organic Wheat Flour 5kg', 'Refined Sunflower Oil 1L', 'Toor Dal 1kg', 'Pink Rock Salt 1kg', 'Raw Cane Sugar 1kg', 'Poha Flakes 500g', 'Extra Virgin Olive Oil 500ml'],
    'Personal Care': ['Hydrating Face Wash 150ml', 'Anti-Dandruff Shampoo 340ml', 'Moisturizing Body Lotion 400ml', 'Herbal Toothpaste 200g', 'Deep Conditioning Hair Mask 200g', 'Sunscreen SPF50 100g', 'Exfoliating Scrub 100ml', 'Bath Soap 3x125g'],
    'Home Care': ['Laundry Pods 30pk', 'Disinfectant Floor Cleaner 2L', 'Dishwash Gel 750ml', 'Fabric Softener 1L', 'Kitchen Degreaser 500ml', 'Air Freshener Spray 300ml', 'Toilet Cleaner Gel 1L', 'Garbage Bags 30pk'],
    'Dairy & Fresh': ['Greek Yogurt 400g', 'Pasteurized Cow Milk 1L', 'Salted Table Butter 500g', 'Paneer Block 200g', 'Cheddar Cheese Slices 200g', 'Dairy Whipping Cream 250ml', 'Probiotic Drink 5x65ml', 'Soy Tofu 200g'],
    'Packaged Food': ['Instant Masala Noodles 280g', 'Rolled Oats 1kg', 'Classic Tomato Ketchup 1kg', 'Durum Wheat Pasta 500g', 'Mayonnaise Spread 400g', 'Choco Crunch Cereal 450g', 'Peanut Butter Crunchy 500g', 'Mixed Fruit Jam 500g'],
    'Household Essentials': ['Kitchen Paper Towels 2pk', 'Aluminium Foil 20m', 'Microfiber Cleaning Cloths 4pk', 'Scented Candle 180g', 'Food Storage Containers 3pk', 'Hand Sanitizer 500ml', 'Steel Scrubber 3pk', 'Lint Roller 60 sheets']
  };

  const skus = Array.from({ length: 800 }, (_, i) => {
    const idNum = i + 1;
    const skuId = `SKU-${String(idNum).padStart(3, '0')}`;
    const category = categories[i % categories.length];
    const templates = productTemplates[category];
    const baseName = templates[i % templates.length];
    const variant = Math.floor(i / templates.length) + 1;
    const name = variant > 1 ? `${baseName} (Batch ${variant})` : baseName;

    const price = Math.round((55 + (i % 55) * 11.5) * 100) / 100;
    const cost = Math.round(price * 0.70 * 100) / 100;
    
    const velocityClass = i % 8 === 0 ? 'Slow Mover' : i % 3 === 0 ? 'Fast Mover' : 'Medium Mover';
    const baseDailyDemand = velocityClass === 'Slow Mover' ? 0.3 : velocityClass === 'Fast Mover' ? 4.2 : 1.9;

    return {
      id: skuId,
      name,
      category,
      price,
      cost,
      velocityClass,
      baseDailyDemand,
      margin: Math.round((price - cost) * 100) / 100
    };
  });

  // 3. Operational Dataset Generator
  // Calibrates 20 distinct anomaly profiles for each store so the Top 20 is always diverse,
  // dynamic, and realistically graded.
  function generateOperationalDataset() {
    const records = [];
    const today = new Date();
    const daysToSimulate = 30;

    // 20 distinct operational anomaly configurations per store
    const anomalyProfiles = [
      { zeroDays: 8, stock: 12, promo: 0, reason: "Positive stock (12 units) with 8-day zero-sales streak", mode: "Shrinkage / Stolen Units", isPhantom: 1 },
      { zeroDays: 7, stock: 18, promo: 1, reason: "Active promotion with zero customer sales across 7 days", mode: "Misplacement on Wrong Shelf", isPhantom: 1 },
      { zeroDays: 6, stock: 9,  promo: 0, reason: "Sales collapsed 100% while recorded on-hand remains static", mode: "Delayed Adjustment", isPhantom: 1 },
      { zeroDays: 6, stock: 24, promo: 0, reason: "Inbound PO recorded but shelf has 0 sales for 6 days", mode: "Receiving Discrepancy", isPhantom: 1 },
      { zeroDays: 5, stock: 15, promo: 1, reason: "High-velocity SKU with persistent 5-day sales stoppage", mode: "Shrinkage / Shoplifting", isPhantom: 1 },
      { zeroDays: 5, stock: 11, promo: 0, reason: "Stock static at 11 units; 0 checkouts against 2.4/day baseline", mode: "Cycle-Count Human Error", isPhantom: 1 },
      { zeroDays: 5, stock: 20, promo: 0, reason: "Inter-store transfer logged; physical shelf facing empty", mode: "Inter-Store Transfer Error", isPhantom: 1 },
      { zeroDays: 4, stock: 8,  promo: 1, reason: "Promotional campaign active with 0 checkout velocity", mode: "Misplacement in Backroom", isPhantom: 1 },
      { zeroDays: 4, stock: 14, promo: 0, reason: "Sales 88% below expected baseline across last 4 days", mode: "Shrinkage / Shoplifting", isPhantom: 1 },
      { zeroDays: 4, stock: 6,  promo: 0, reason: "End-of-life SKU with residual positive system stock", mode: "Delisted / Discontinued", isPhantom: 0 },
      { zeroDays: 4, stock: 16, promo: 0, reason: "Fast-moving staples line halted abruptly with positive stock", mode: "Misplacement on Wrong Shelf", isPhantom: 1 },
      { zeroDays: 3, stock: 22, promo: 1, reason: "Weekend promotional demand spike failed to register sales", mode: "Receiving Discrepancy", isPhantom: 1 },
      { zeroDays: 3, stock: 10, promo: 0, reason: "Unexplained sales drop: expected 3.1/day, observed 0", mode: "Shrinkage / Stolen Units", isPhantom: 1 },
      { zeroDays: 3, stock: 13, promo: 0, reason: "System stock unchanged across 5 days with zero movement", mode: "Delayed Adjustment", isPhantom: 0 },
      { zeroDays: 3, stock: 7,  promo: 0, reason: "Shelf audit recommended: stock static with low sales", mode: "Cycle-Count Human Error", isPhantom: 0 },
      { zeroDays: 3, stock: 19, promo: 1, reason: "Promotional item experiencing secondary facing blockage", mode: "Misplacement on Shelf", isPhantom: 0 },
      { zeroDays: 2, stock: 11, promo: 0, reason: "Sudden velocity collapse on top-selling beverage", mode: "Shrinkage / Shoplifting", isPhantom: 0 },
      { zeroDays: 2, stock: 15, promo: 0, reason: "Inventory record mismatch: physical check warranted", mode: "Mixed Variance Drift", isPhantom: 0 },
      { zeroDays: 2, stock: 8,  promo: 1, reason: "Promo discount active but scanning frequency halved", mode: "Misplacement on Wrong Shelf", isPhantom: 0 },
      { zeroDays: 2, stock: 6,  promo: 0, reason: "Intermittent slow-mover nearing audit re-count threshold", mode: "Slow Mover Baseline", isPhantom: 0 }
    ];

    stores.forEach((store, sIdx) => {
      // Pick 40 SKUs per store
      const storeSKUs = [];
      for (let k = 0; k < 40; k++) {
        const skuIndex = (sIdx * 23 + k * 13) % skus.length;
        storeSKUs.push(skus[skuIndex]);
      }

      for (let d = daysToSimulate - 1; d >= 0; d--) {
        const curDate = new Date(today);
        curDate.setDate(curDate.getDate() - d);
        const dateStr = curDate.toISOString().slice(0, 10);
        const isWeekend = curDate.getDay() === 0 || curDate.getDay() === 6;

        storeSKUs.forEach((sku, skuPos) => {
          let unitsSold = 0;
          let onHandQty = 0;
          let label = 0;
          let failureMode = 'Normal';
          let customReason = '';

          // The first 20 SKUs represent graduated anomaly cases for this store
          if (skuPos < 20) {
            const profile = anomalyProfiles[skuPos];
            const isInsideZeroStreak = (d < profile.zeroDays);
            const isPromo = (d % 7 === 2 || d % 7 === 3);

            if (isInsideZeroStreak) {
              unitsSold = 0;
              onHandQty = profile.stock;
              label = profile.isPhantom;
              failureMode = profile.mode;
              customReason = profile.reason;
            } else {
              // Prior normal sales before phantom wiped it out
              const base = sku.baseDailyDemand * (isWeekend ? 1.3 : 0.95);
              unitsSold = Math.max(1, Math.round(base + (d % 3) * 0.4));
              onHandQty = profile.stock + Math.round((d - profile.zeroDays) * base * 0.6);
            }

            records.push({
              date: dateStr,
              store_id: store.id,
              sku_id: sku.id,
              product: sku.name,
              category: sku.category,
              price: sku.price,
              cost: sku.cost,
              velocityClass: sku.velocityClass,
              units_sold: unitsSold,
              on_hand_qty: onHandQty,
              promotion: isPromo ? 1 : 0,
              label,
              failureMode,
              customReason
            });
          } else {
            // Normal healthy SKUs
            const isPromo = (d % 14 === 4);
            const base = sku.baseDailyDemand * (isWeekend ? 1.35 : 0.9) * (isPromo ? 1.5 : 1.0);
            const noise = ((d + sku.id.charCodeAt(5)) % 5) * 0.3 - 0.4;

            if (sku.velocityClass === 'Slow Mover') {
              unitsSold = (d % 3 === 0) ? Math.max(1, Math.round(base)) : 0;
            } else {
              unitsSold = Math.max(1, Math.round(base + noise));
            }

            onHandQty = Math.max(unitsSold + 4, 26 - (d % 12) * 2);
            label = 0;

            records.push({
              date: dateStr,
              store_id: store.id,
              sku_id: sku.id,
              product: sku.name,
              category: sku.category,
              price: sku.price,
              cost: sku.cost,
              velocityClass: sku.velocityClass,
              units_sold: unitsSold,
              on_hand_qty: onHandQty,
              promotion: isPromo ? 1 : 0,
              label: 0,
              failureMode: 'Normal',
              customReason: ''
            });
          }
        });
      }
    });

    return records;
  }

  const dataset = generateOperationalDataset();

  return {
    stores,
    skus,
    dataset,
    profile: {
      months: 18,
      skuCatalogCount: 800,
      storeNetworkCount: 25,
      hiddenLabelRate: '~3%',
      dailyVerificationCap: 20
    }
  };
})();
