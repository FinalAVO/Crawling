const express = require('express');
const bodyParser = require('body-parser');
// const CircularJSON = require('circular-json');
const app = express();
const {PythonShell} =require('python-shell');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : false}));

const { Client } = require('node-scp');
const fs = require('fs')
const shell = require('shelljs');

app.get("/scrap",(req, res, next) => {
  var app_name = req.query.app_name

  if (!app_name) {
    res.send("Empty App Name");
  }
  else{
    // scraping apple App Store reviews
    let options = {
          mode: 'text',
          pythonOptions: ['-u'],
          args: [app_name] //sys.argv[1]
    };

    PythonShell.run('apple.py', options, function (err, result){
            if (err) throw err;

    });


    PythonShell.run('google.py', options, function (err, result){
            if (err) throw err;

    });

    setTimeout(() => shell.exec('sh /data/Crawling/shell_file/mongo.sh ' + app_name), 15000);


    // send file with scp
    var local_file_path = './result/app_review_final.csv';
    var destination_file_path = '/data/node/review/result/app_review_final.csv';

    async function send_file() {
      try {
        const client = await Client({
          host: '3.39.5.86',
          port: 22,
          username: 'bitnami',
          password: '',
          privateKey: fs.readFileSync('/data/Crawling/Lightsail_mysql.pem'),
        })
        await client.uploadFile(local_file_path, destination_file_path)
        client.close()
      } catch (e) {
        console.log(e)
      }
    }

    // send particular review files to mysql server
    setTimeout(() => send_file(), 18000);

    res.send("Crawling Done");
  }


});




module.exports = app;
