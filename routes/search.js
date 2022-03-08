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
	var sc;
	if(!condition){
		condition = "DATE";
	}else if (condition.indexOf('-') != -1) {
		sc = -1;
		condition = condition.slice(1);
	}else{
		sc = 1;
	}

	mongoClient.connect(databaseUrl, function(err, database){
		if(err){
			console.error(err);
			console.log("connection error...!");
			res.json("connection error...!");
		}else{
			db = database.db('review');
			if(!filter){
				db.collection(app_name).find({ }, { _id: 0 }).sort({ [condition]: sc }).toArray(function(err, result){
					if(err) throw err;
					console.log('review : ' + result);
					res.send(JSON.stringify(result));
				});
			}else{
				db.collection(app_name).find({ COMMENT: filter }, { _id: 0 }).sort({ [condition]: sc }).toArray(function(err, result){
					if(err) throw err;
					console.log('result : ' + result);
					res.send(JSON.stringify(result));
				});
			}
		}
	})
});

module.exports = app;
