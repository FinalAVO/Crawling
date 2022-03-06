const express = require('express')
const mongoClient = require('mongodb').MongoClient

const app = express();

var db;
var databaseUrl = 'mongodb://localhost:46171/'

app.get('/', (req, res) => {
	var app_name = req.query.app_name;
  console.log(app_name);
	var filter = req.query.filter;
	if(!filter){
		filter = null;
	}

	var condition = req.query.condition;
	if(!condition){
		condition = "DATE";
	}

	mongoClient.connect(databaseUrl, function(err, database){
		if(err){
			console.error(err);
			console.log("connection error...!");
			res.json("connection error...!");
		}else{
			db = database.db('review');
			if(!filter){
				db.collection('오딘').find({ APP_NAME: { $regex: app_name, $options: "i"} }, { _id: 0 }).sort({ [condition]: 1 }).toArray(function(err, result){
					if(err) throw err;
					console.log('review : ' + result);
					res.send(JSON.stringify(result));
				});
			}else{
				db.collection('오딘').find({ APP_NAME:  { $regex: app_name, $options: "i"}, COMMENT: filter }, { _id: 0 }).sort({ [condition]: 1 }).toArray(function(err, result){
					if(err) throw err;
					console.log('result : ' + result);
					res.send(JSON.stringify(result));
				});
			}
		}
	})
});

module.exports = app;
