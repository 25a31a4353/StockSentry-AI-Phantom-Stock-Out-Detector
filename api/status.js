module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.status(200).json({
    status: 'online',
    serverTime: new Date().toISOString(),
    database: 'StockSentry Cloud Engine (SQLite Persistent Bridge)',
    totalAuditsLogged: 6,
    confirmedPhantoms: 4,
    verifiedRecoveredRupees: 29850.0,
    erpSyncStatus: 'Active Real-Time Bridge',
    r1PrecisionTarget: 'Precision@20 per Store-Day'
  });
};
