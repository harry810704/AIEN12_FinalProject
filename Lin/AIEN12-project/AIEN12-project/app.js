'use strict';
var port = process.env.PORT || 3000;
var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var path = require('path')
var session = require('express-session');
app.use(session({ secret: 'test', name: "user", cookie: { maxAge: 60000000000000 } }));
app.set('view engine', 'ejs');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

var main = require('./service/main.js');
var sql = require('./service/sql.js');
var bot = require('./service/bot.js');
app.use("/", main);
app.use("/sql", sql);
app.use("/bot", bot);
app.listen(port);