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

// send file with scp
var local_file_path = './data/apple_review.csv';
var destination_file_path = '/data/node/review/data/apple_review.csv';

async function send_file() {
  try {
    const client = await Client({
      host: '3.39.5.86',
      port: 22,
      username: 'bitnami',
      password: '',
      privateKey: fs.readFileSync('../LightsailDefaultKey-ap-northeast-2.pem'),
    })
    await client.uploadFile(local_file_path, destination_file_path)
    client.close()
  } catch (e) {
    console.log(e)
  }
}

app.get("/scrap/google",(req, res) => {
  // shell.exec('sh scraping.sh')
  // shell.exec('sh export_mongo.sh')
  // send_file()
  res.send("Google Done");

});

app.get("/scrap",(req, res, next) => {
  var app_name = req.query.app_name
  console.log(app_name)
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
            // res.json({result: result.toString()});
            res.send("Apple Done");
    });

    // send particular review files to mysql server
    // send_file()
  }


});






module.exports = app;
