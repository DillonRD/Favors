
const router = require('express').Router();

const homeRoutes = require('./homeRoutes.js');
const api = require('./api');
const dashboardRoute = require('./dashboardRoute.js');

router.use('/', homeRoutes);
router.use('/api', api);
router.use('/dashboard', dashboardRoute);

module.exports = router; 