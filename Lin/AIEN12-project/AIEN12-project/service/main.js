var express = require('express');
var api = express.Router();

api.route('/').get(function (req, res, next) {
    res.render('pages/index');
})

api.route('/photoshow').get(function (req, res, next) {
    var p_id = Object.keys(req.query)[0]
    res.render('pages/photoshow', { p_id: p_id});
})

api.route('/add').get(function (req, res, next) {
    res.render('pages/add');
})

module.exports = api;