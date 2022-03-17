const express = require('express');
const bodyParser = require('body-parser');
const {PythonShell} =require('python-shell');
const request = require('request');
const fs = require('fs')
const shell = require('shelljs');
const mysql = require('mysql');
const axios = require('axios');

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : false}));

let mysql_rawdata = fs.readFileSync('/data/Crawling/config/mysql.json');
let mysql_json = JSON.parse(mysql_rawdata);

var connection = mysql.createConnection({
  host     : mysql_json["host"],
  user     : mysql_json["user"],
  password : mysql_json["password"],
  database : mysql_json["database"]
});


// 앱을 RDS crawling_log에서 찾기 위한 API
app.get("/scrap", function(req, res){
  var app_name = req.query.app_name
  var filter = req.query.filter;
  var condition = req.query.condition;
  var os = req.query.os

  if (!app_name) {
    console.log("Empty App Name");
    res.send("Empty App Name");
  }

  let options = {
        mode: 'text',
        pythonOptions: ['-u'],
        args: [app_name]
  };

  console.log("Finding app_id ... \n");

  get_app_name(options, function(apple_app_id, google_app_id, app_name_for_db, real_app_name){

    connection.connect(function(err){
      if(!err) {
          console.log("RDS is connected ... \n");
      } else {
          console.log("Error connecting RDS ... \n");
      }
    });

    console.log("Searching thru log table");

    sql = 'SELECT * FROM crawling_log WHERE app_name LIKE ?';
    var app_name_sql = '%' + app_name + '%'
    connection.query(sql, [app_name_sql], function(err, result){
      // connection.end();
      if(err){
        console.log('Error while performing Query.');
        res.send("Error while performing Query.")
      }

      if(result == ''){
        // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재하지 않는다면
        console.log("Not Found on log table ... \nCrawling started ... \n");

        axios.post("http://3.34.14.98:3000/crawl", {
            apple_app_id: apple_app_id,
            google_app_id: google_app_id,
            app_name_for_db: app_name_for_db,
            real_app_name: real_app_name
        })
        .then(function (response) {
        	res.send(response.data);
        })
        .catch(function (error) {
        	console.log(error);
        });

      } else {
        // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재한다면
        // app_name_for_db를 res로 보내고 다시 app_name_for_db, filter, condition을 쿼리로 search.js로 넘겨주는 펑션 쓰기 (프론트에)
        console.log("Already exist in log table ... \n");
        res.send(app_name_for_db);
      }

    });
  });
});

app.post("/crawl", function(req, res){

  var apple_app_id = req.body.apple_app_id;
  var google_app_id = req.body.google_app_id;
  var app_name_for_db = req.body.app_name_for_db;
  var real_app_name = req.body.real_app_name;

  let options_apple = {
        mode: 'text',
        pythonOptions: ['-u'],
        args: [apple_app_id, real_app_name]
  };

  crawl_apple(options_apple, function(message){
    if (message == 'Apple Done'){
      console.log("Apple Done");
      shell.exec('sh /data/Crawling/shell_file/mongo_apple.sh ' + app_name_for_db);
    } else {
      console.log("Something wrong with Apple crawling");
    }
  });

  let options_google = {
        mode: 'text',
        pythonOptions: ['-u'],
        args: [google_app_id]
  };

  crawl_google(options_google, function(message){
    if (message == 'Google Done'){
      console.log("Google Done");

      shell.exec('sh /data/Crawling/shell_file/mongo_google.sh ' + app_name_for_db);

      // app_name_for_db를 res로 보내고 다시 app_name_for_db, filter, condition을 쿼리로 search.js로 넘겨주는 펑션 쓰기 (프론트에)
      // var url = 'http://3.34.14.98:3000/search?app_name_for_db=' + app_name_for_db + '&filter=' + filter + '&condition=' + condition;

      axios.post("http://3.34.14.98:3000/insert", {
          app_name_for_db: app_name_for_db,
      })
      .then(function (response) {
        res.send(response.data);
        // console.log("/crawl : " + response.data);
      })
      .catch(function (error) {
        console.log(error);
      });

    } else {
      console.log("Something wrong with Google crawling");
    }
  });
});

app.post("/insert", function(req,res){
  var app_name_for_db = req.body.app_name_for_db;

  insert_RDS(app_name_for_db, function(message){
    if (message == "crawling_log insert succeeded"){
      console.log("Crawling succeeded");
      res.send(app_name_for_db);
    } else {
      res.send("failed")
    }
  });
});


let get_app_name = function(options, callback){
  PythonShell.run('./python_script/app_id.py', options, function (err, result){
          if (err) throw err;
          callback(result[0], result[1], result[2], result[3]);
  });
}

let crawl_apple = function(options, callback){
  PythonShell.run('./python_script/apple.py', options, function (err, result){
          if (err) throw err;
          callback(result);
  });
}

let crawl_google = function(options, callback){
  PythonShell.run('./python_script/google.py', options, function (err, result){
          if (err) throw err;
          callback(result);
  });
}

let insert_RDS = function (app_name_for_db, callback){
  // RDS테이블에 app_name_for_db와 현재 시간 넣기
  var sql = 'INSERT INTO crawling_log (app_name) VALUES (?);';
  // 한국시간으로 바꾸기
  // var timestamp = new Date().toISOString();
  // console.log(timestamp);

  connection.query(sql, [app_name_for_db], function(err, result){
    if(err) {
      console.log("crawling_log insert failed")
      callback("crawling_log insert failed")
    } else {
      console.log("crawling_log insert succeeded")
      callback("crawling_log insert succeeded")
    }
  });
}

module.exports = app;
