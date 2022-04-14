const express = require('express');
const bodyParser = require('body-parser');
const {PythonShell} =require('python-shell');
const request = require('request');
const fs = require('fs')
const shell = require('shelljs');
const mysql = require('mysql');
const axios = require('axios');
const { createClient } = require('redis');
const moment = require('moment-timezone');

const EventEmitter = require('events');
const util = require('util');
function MyEmitter() {
EventEmitter.call(this);
}
util.inherits(MyEmitter, EventEmitter);
const myEmitter = new MyEmitter();
myEmitter.setMaxListeners(20)
const app = express();


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : false}));

let mysql_rawdata = fs.readFileSync('/data/Crawling/config/rds_config.json');
let mysql_json = JSON.parse(mysql_rawdata);

const rdsConnection = mysql.createConnection({
host     : mysql_json["host"],
user     : mysql_json["user"],
password : mysql_json["password"],
database : mysql_json["database"]
});

const redisClient = createClient({
url: 'redis://:1234@3.37.3.24:6379'
});

app.post("/register", function(req,res){
var user_id = req.body.user_id
var app_name = req.body.app_name

let options = {
  mode: 'text',
  pythonOptions: ['-u'],
  args: [app_name]
};

register_id(options, function(real_app_name, app, app_img){

  var sql2 = 'SELECT * FROM user_app WHERE user_id = ? and db_name = ?'
  rdsConnection.query(sql2, [user_id, app], function(err, result2){

    if (result2.length > 0){
      res.send("Already exist");
    } else {
      var sql = 'INSERT INTO user_app (user_id, app_name, db_name, app_img) VALUES (?, ?, ?, ?);';

      rdsConnection.query(sql, [user_id, real_app_name, app, app_img], function(err, result){
        if(err) {
          res.send("failed to register app")
        } else {
          res.send("app successfully registered")
        }
      });
    }
  })
})
});

// 앱을 RDS crawling_log에서 찾기 위한 API
app.get("/scrap", function(req, res){
var app_name = req.query.app_name
// var filter = req.query.filter;
// var condition = req.query.condition;
// var os = req.query.os

if (!app_name) {
  console.log("Empty App Name");
  res.send("Empty App Name");
} else{
  let options = {
    mode: 'text',
    pythonOptions: ['-u'],
    args: [app_name]
  };

  console.log("Finding app_id ... \n");

  get_app_name(options, function(apple_app_id, google_app_id, app_name_for_db, real_app_name){

    // rdsConnection.connect(function(err){
    //   if(!err) {
    //       console.log("RDS is connected ... \n");
    //   } else {
    //       console.log("Error connecting RDS ... \n");
    //   }
    // });
    if (apple_app_id == "SSL issue"){
      res.send("SSL issue")
    } else {
      console.log("Searching thru log table");

      sql = 'SELECT * FROM crawling_log WHERE app_name = ?';

      rdsConnection.query(sql, [app_name_for_db], function(err, result){
        // rdsConnection.end();
        if(err){
          console.log('Error while performing Query.');
          res.send("Error while performing Query.")
        }

        if(result == ''){
          // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재하지 않는다면
          console.log("Not Found on log table ... ");

          checking_redis(app_name_for_db, function(message){
            if (message == "Already in progress"){
              console.log(message)

              res.send("Already in progress")

            } else {
              console.log(message)

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
            }
          });


        } else {
          // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재한다면
          console.log("Already exist in log table ... \n");
          console.log(app_name_for_db);
          res.send(app_name_for_db);
        }

      }); //lll
     }
  });
}
});

app.get("/report_crawl", function(req, res){
  var app_name_for_db = req.query.db_name;
  var app_name = req.query.app_name;
  sql = 'SELECT * FROM crawling_log WHERE app_name = ?';

  rdsConnection.query(sql, [app_name_for_db], function(err, result){
    // rdsConnection.end();
    if(err){
      console.log('Error while performing Query.');
      res.send("Error while performing Query.")
    }

    let options = {
      mode: 'text',
      pythonOptions: ['-u'],
      args: [app_name]
    };

    console.log("Finding app_id ... \n");

    get_app_name(options, function(apple_app_id, google_app_id, app_name_for_db, real_app_name){

      // rdsConnection.connect(function(err){
      //   if(!err) {
      //       console.log("RDS is connected ... \n");
      //   } else {
      //       console.log("Error connecting RDS ... \n");
      //   }
      // });
      if (apple_app_id == "SSL issue"){
        res.send("SSL issue")
      } else {
        console.log("Searching thru log table");

        sql = 'SELECT * FROM crawling_log WHERE app_name = ?';

        rdsConnection.query(sql, [app_name_for_db], function(err, result){
          // rdsConnection.end();
          if(err){
            console.log('Error while performing Query.');
            res.send("Error while performing Query.")
          }

          if(result == ''){
            // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재하지 않는다면
            console.log("Not Found on log table ... ");

            checking_redis(app_name_for_db, function(message){
              if (message == "Already in progress"){
                console.log(message)

                res.send("Already in progress")

              } else {
                console.log(message)

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
              }
            });


          } else {
            // 만약 크롤링 로그 테이블에 전처리된 app_name이 존재한다면
            console.log("Already exist in log table ... \n");
            console.log(app_name_for_db);
            res.send(app_name_for_db);
          }
        });
      }
    });
  })
})

app.post("/crawl", function(req, res){

  var apple_app_id = req.body.apple_app_id;
  var google_app_id = req.body.google_app_id;
  var app_name_for_db = req.body.app_name_for_db;
  var real_app_name = req.body.real_app_name;

  (async () => {
    console.log("/crawl API");

    redisClient.on('error', (err) => console.log('Redis Client Error', err));

    await redisClient.connect();

    await redisClient.set(app_name_for_db, 'working');
    await redisClient.expire(app_name_for_db, 60);
    redisClient.quit();
  })();

  let options_apple = {
    mode: 'text',
    pythonOptions: ['-u'],
    args: [apple_app_id, real_app_name, "crawl", app_name_for_db]
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
    args: [google_app_id, "crawl", app_name_for_db]
  };

  crawl_google(options_google, function(message){
    if (message == 'Google Done'){
      console.log("Google Done");

      shell.exec('sh /data/Crawling/shell_file/mongo_google.sh ' + app_name_for_db);

      axios.post("http://3.34.14.98:3000/insert", {
        app_name_for_db: app_name_for_db,
        apple_app_id: apple_app_id,
        google_app_id: google_app_id,
        real_app_name: real_app_name
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
  var apple_app_id = req.body.apple_app_id;
  var google_app_id = req.body.google_app_id;
  var real_app_name = req.body.real_app_name;

  insert_RDS(app_name_for_db, apple_app_id, google_app_id, real_app_name, function(message){
    if (message == "crawling_log insert succeeded"){
      console.log("Crawling succeeded");
      res.send(app_name_for_db);
    } else {
      res.send("failed")
    }
  });
});


let checking_redis = function(app_name_for_db, callback){
  (async () => {
    console.log("Check in redis ... ");

    redisClient.on('error', (err) => console.log('Redis Client Error', err));

    await redisClient.connect();

    const value = await redisClient.get(app_name_for_db);
    var message;

    if (value == "working"){
      redisClient.quit();
      message = "Already in progress"
      callback(message);
    } else{
      redisClient.quit();
      message = "Not in progress"
      callback(message)
    }
  })();
}

let get_app_name = function(options, callback){
  PythonShell.run('/data/Crawling/python_script/app_id.py', options, function (err, result){
    if (err) throw err;
    callback(result[0], result[1], result[2], result[3]);
  });
}

let register_id = function(options, callback){
  PythonShell.run('/data/Crawling/python_script/register_id.py', options, function (err, result){
    if (err) throw err;
    callback(result[0], result[1], result[2]);
  });
}

let crawl_apple = function(options, callback){
  PythonShell.run('/data/Crawling/python_script/apple.py', options, function (err, result){
    if (err) throw err;
    callback(result);
  });
}

let crawl_google = function(options, callback){
  PythonShell.run('/data/Crawling/python_script/google.py', options, function (err, result){
    if (err) throw err;
    callback(result);
  });
}

let insert_RDS = function (app_name_for_db, apple_app_id, google_app_id, real_app_name, callback){
  // RDS테이블에 app_name_for_db와 현재 시간 넣기
  var sql = 'INSERT INTO crawling_log (app_name, apple_app_id, google_app_id, real_app_name) VALUES (?, ?, ?, ?);';

  // 한국시간으로 바꾸기
  // var time = moment.tz(new Date(), 'Asia/Seoul').format()


  rdsConnection.query(sql, [app_name_for_db, apple_app_id, google_app_id, real_app_name], function(err, result){
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
