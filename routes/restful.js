const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const {PythonShell} =require('python-shell');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : false}));

const { Client } = require('node-scp');
const fs = require('fs')
const shell = require('shelljs');

app.get("/scrap",(req, res) => {
  res.send("Crawling Done");
});

var local_file_path = './data/app_review.csv';
var destination_file_path = '/data/node/review/data/app_review.csv';

async function send_file() {
  try {
    const client = await Client({
      host: '3.39.5.86', //remote host ip
      port: 22, //port used for scp
      username: 'bitnami', //username to authenticate
      password: '', //password to authenticate
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
  res.send("Crawling Done");

});

app.get("/scrap/url",(req, res, next) => {

  const url = req.query.url_id
  let options = {
        mode: 'text',
        pythonOptions: ['-u'], // get print results in real-time
        args: [url] //An argument which can be accessed in the script using sys.argv[1]
  };
  //
  PythonShell.run('test.py', options, function (err, result){
          if (err) throw err;
          // console.log('result: ', result.toString());
          res.json({result: result.toString()});
  });
});






module.exports = app;
