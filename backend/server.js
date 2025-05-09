require('dotenv').config();
const express = require('express');
const movies = require('./routes/movies');

const app = express();
app.use(express.json());

app.use('/api', movies);

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

const PORT = 3000
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});