const express = require('express');
const app = express();
const path = require('path');

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname,  'index.html'));
});

app.listen(5432, () => {
  console.log('Server is running on port 5432');
});

