require('dotenv').config();
const express = require('express');
const router = express.Router();

const API_KEY = process.env.TMDB_AUTH_KEY;
const BASE_URL = 'https://api.themoviedb.org/3';

// Get the list of all trending movies
router.get('/movies', async (req, res) => {
    try {
        const url = `${BASE_URL}/movie/now_playing?language=en-US&page=1`;
        const options = {
            method: 'GET',
            headers: {
                accept: 'application/json',
                Authorization: `Bearer ${API_KEY}`,
            },
        };
        const response = await fetch(url, options);
        const data = await response.json();
        console.log('Trending movies:', data);
        res.json(data);
    } catch (error) {
        console.error('Error fetching trending movies:', error);
        res.status(500).json({ error: 'Failed to fetch trending movies' });
    }
});
// Get the details of a specific movie by ID
router.get('/movies/:id', async (req, res) => {
    const movieId = req.params.id;
    try {
        const url = `${BASE_URL}/movie/${movieId}?language=en-US`;
        const options = {
            method: 'GET',
            headers: {
                accept: 'application/json',
                Authorization: `Bearer ${API_KEY}`,
            },
        };
        const response = await fetch(url, options);
        const data = await response.json();
        console.log('Movie details:', data);
        res.json(data);
    } catch (error) {
        console.error('Error fetching movie details:', error);
        res.status(500).json({ error: 'Failed to fetch movie details' });
    }
});
// Get list of upcoming movies
router.get('/movies/upcoming', async (req, res) => {
    try {
        const url = `${BASE_URL}/movie/upcoming?language=en-US&page=1`;
        const options = {
            method: 'GET',
            headers: {
                accept: 'application/json',
                Authorization: `Bearer ${API_KEY}`,
            },
        };
        const response = await fetch(url, options);
        const data = await response.json();
        console.log('Upcoming movies:', data);
        res.json(data);
    } catch (error) {
        console.error('Error fetching upcoming movies:', error);
        res.status(500).json({ error: 'Failed to fetch upcoming movies' });
    }
});

module.exports = router;