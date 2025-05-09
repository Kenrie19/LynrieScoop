const express = require('express');
const { authenticate, requireManager } = require('../middleware/authentication');
const router = express.Router();