var express = require('express');
var api = express.Router();

api.route('/').get(function (req, res, next) {
    res.render('pages/bot');
})

module.exports = api;