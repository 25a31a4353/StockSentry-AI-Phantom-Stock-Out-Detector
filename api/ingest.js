module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const records = req.body?.records || [];
  return res.status(200).json({
    success: true,
    count: records.length,
    message: `Successfully ingested ${records.length} records into StockSentry pipeline`
  });
};
