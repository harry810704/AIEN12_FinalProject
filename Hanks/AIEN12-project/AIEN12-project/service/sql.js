var express = require('express');
var api = express.Router();
var mysql = require('mysql');
var fs = require('fs');
var spawn = require("child_process").spawn
var exec = require('child_process').exec;
const nodecallspython = require("node-calls-python");
let py = nodecallspython.interpreter;
require('@tensorflow/tfjs').version
var con = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "AIEN12",
    database: "medical"
});

//登入時在欄位內輸入會透過這裡對資料庫查詢包含你輸入的字的結果並回傳
api.route('/inquire').post(function (req, res, next) {
    var m_card = req.body.m_card;
    var sql = "SELECT `m_card` FROM `member` where m_card like '%" + m_card + "%';";
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json(result);
        }
    });
})

//登入
api.route('/search').post(function (req, res, next) {
    var m_card = req.body.m_card;
    var sql = "SELECT * FROM `member` where m_card = '" + m_card + "';";
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            if (result.length == 0) {
                res.json("1");
            } else {
                req.session.user = result[0]['m_id']
                res.json(result);
            }
        }
    });
})

//病人基本資料
api.route('/data').post(function (req, res, next) {
    var m_id = req.session.user;
    var sql = "SELECT * FROM `member` where m_id = '" + m_id + "';";
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json(result);
        }
    });
})

//X光片下拉選單日期查詢
api.route('/select').post(function (req, res, next) {
    var m_id = req.session.user;
    var sql = "SELECT DATE_ADD(`p_date`,INTERVAL 1 DAY) as `date` FROM `photo` where m_id = '" + m_id+"';";
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json(result);
        }
    });
})

//查詢X光片
api.route('/photosearch').post(function (req, res, next) {
    var m_id = req.session.user;
    var p_date = req.body.p_date
    
    var sql = "SELECT DATE_ADD(`p_date`,INTERVAL 1 DAY) as `date`,`p_name`,`p_id` FROM `photo` where `m_id` = '" + m_id + "' and `p_date` BETWEEN '" + p_date +"' and CURDATE();";
    
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json(result);
        }
    });
})

//X光片比對照片查詢
api.route('/photoshowsearch').post(function (req, res, next) {
    var m_id = req.session.user;
    var p_id = req.body.p_id

    var sql = "select *,DATE_ADD(`p_date`,INTERVAL 1 DAY) as `date` from `photo` where `m_id`='" + m_id + "' and  `p_date`=(select `p_date` from `photo` where `p_id`='" + p_id+"') or `p_date`=(select max(`p_date`) from `photo` )";
 
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json(result);
        }
    });
})

//開啟模組
api.route('/open_python').post(function (req, res, next) {
    const python = spawn('python', ['../AIEN12-python/Project/Model1.py',req.body.img_name]);
    python.stdout.on('data', function (data) {
        const parsedString = JSON.parse(data)
        console.log(parsedString)
        res.json(parsedString)
    });
})


//新增病人資料
api.route('/add').post(function (req, res, next) {
    console.log(req.body)
    var sql = "INSERT INTO `medical`.`member` (`m_name`, `m_card`, `m_birthday`, `m_history`, `m_cellphone`, `m_address`, `m_gender`, `m_phone1`, `m_phone2`, `m_blood`, `m_marriage`, `m_child`, `m_education`, `m_jobs`, `m_allergy`, `m_smokes`, `m_areca`, `m_wine`) VALUES ('" + req.body.name + "', '" + req.body.mid + "', '" + req.body.date + "', '" + req.body.history + "', '" + req.body.cellphone + "', '" + req.body.address + "', '" + req.body.sex + "', '" + req.body.phone1 + "', '" + req.body.phone2 + "', '" + req.body.blood + "', '" + req.body.marriage + "', '" + req.body.child + "', '" + req.body.education + "', '" + req.body.jobs + "', '" + req.body.allergy + "', '" + req.body.smokes + "', '" + req.body.areca + "', '" + req.body.wine+"');"
    con.query(sql, function (err, result, next) {
        if (err) {
            console.log(err);
        } else {
            res.json("1");
        }
    });
})

module.exports = api;