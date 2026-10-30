module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  return res.status(200).json({
    outcomes: {
      "Confirmed Phantom Stock-Out": 4,
      "Misplaced on Wrong Shelf": 1,
      "Stock Actually Present": 1
    },
    mttdDays: 2.3,
    erpReorderLatencyHours: 3.8,
    topShrinkageStores: ["S01 (Hyderabad)", "S04 (Chennai)", "S07 (Vijayawada)", "S12 (Kochi)"]
  });
};

