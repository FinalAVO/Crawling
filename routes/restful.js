const express = require('express');
const bodyParser = require('body-parser');

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : false}));

const spawn = require('child_process').spawn;
const {PythonShell} =require('python-shell');

app.get("/scrap",(req, res) => {
  res.send("Hello");
});

app.get("/scrap/url",(req, res, next) => {
  // var process = spawn('python', ['test.py']);
  // process.stdout.on('data', function(data) {
  //
  //   console.log('started');
  //   res.send(data.toString());
  //   res.end('end');
  // });

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







// const users = [
//   { id:1, name: "User1" },
//   { id:2, name: "User2" },
//   { id:3, name: "User3" }
// ];

// // simple api
// app.get("/Hello",(req, res) => {
//   res.send("Hello World");
// });
//
// // request param X, response O
// app.get("/api/users",(req, res) => {
//   res.json({ok:true, users:users});
// });
//
// // query paramter, request param O, response O
// app.get("/api/users/user",(req, res) => {
//   const user_id = req.query.user_id
//   const user = users.filter(data => data.id == user_id);
//   res.json({ok:false, users:user});
// });
//
// // path param, request param O, response O
// app.get("/api/users/:user_id",(req, res) => {
//   const user_id = req.params.user_id
//   const user = users.filter(data => data.id == user_id);
//   res.json({ok:true, users:user});
// });
//
// // post, request body, response O
// app.post("/api/users/userBody",(req, res) => {
//   const user_id = req.body.id
//   const user = users.filter(data => data.id == user_id);
//   res.json({ok:true, users:user});
// });
//
// // post, request body, response O
// app.post("/api/users/add",(req, res) => {
//   const { id, name } = req.body
//   const user = users.concat({id, name});
//   res.json({ok:true, users:user});
// });
//
// // put, request body, response O
// app.put("/api/users/update",(req, res) => {
//   const { id, name } = req.body
//   const user = users.map(data => {
//     if(data.id == id) data.name = name
//     return {
//       id: data.id,
//       name: data.name
//     }
//   });
//   res.json({ok:true, users:user});
// });
//
// // patch, request path param & body, response O
// app.patch("/api/user/update/:user_id",(req, res) => {
//   const { user_id } = req.params
//   const { id, name } = req.body
//   const user = users.map(data => {
//     if(data.id == user_id) data.name = name
//     return {
//       id: data.id,
//       name: data.name
//     }
//   });
//   res.json({ok:true, users:user});
// });
//
// // delete, request body, response O
// app.delete("/api/user/delete",(req, res) => {
//   const { user_id } = req.body
//   const user = users.filter(data => data.id != user_id);
//   res.json({ok:true, users:user});
// });









module.exports = app;
