var firebase = require("firebase");
var fs = require("fs");
var flightNum;
var name;
var experience;
var keywords;
var counter;
var avgScore;
var exitBool = false;
var exists = false;
firebase.initializeApp({
  serviceAccount: "Aviato-f75004767347.json",
  databaseURL: "https://aviato-e3fc4.firebaseio.com/"
});
var db = firebase.database();
var ref = db.ref("server");
var filename = "./data.txt";
fs.readFile(filename, 'utf8', function(err, contents) {
  var arr = (CSVToArray(contents, ';'));
  flightNum = arr[0];
  name = arr[1];
  experience = arr[2];
  keywords = (CSVToArray(arr[3], ','));
  score = parseFloat(arr[4]);
});
function CSVToArray(strData, strDelimiter ){
        strDelimiter = (strDelimiter);
        var objPattern = new RegExp(
            (
                // Delimiters.
                "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +
                // Quoted fields.
                "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +
                // Standard fields.
                "([^\"\\" + strDelimiter + "\\r\\n]*))"
            ),
            "gi"
            );
        var arrData = [];
        var arrMatches = null;
        while (arrMatches = objPattern.exec( strData )){
            var strMatchedDelimiter = arrMatches[ 1 ];
            if (
                strMatchedDelimiter.length &&
                (strMatchedDelimiter != strDelimiter)
                ){
                arrData.push( [] );
            }
            if (arrMatches[ 2 ]){
                var strMatchedValue = arrMatches[ 2 ].replace(
                    new RegExp( "\"\"", "g" ),
                    "\""
                    );
            } else {
                // We found a non-quoted value.
                var strMatchedValue = arrMatches[ 3 ];
            }
            arrData.push( strMatchedValue );
        }
        return(arrData);
    }
ref.on("value", function(snapshot) {
  if (exitBool) {
    process.exit();
  }
  var obj = snapshot.val();
  for (var key in obj) {
    if (key == flightNum && !exists) {
      exists = true;
      var nObj = obj[key];
      var scr = nObj['avgScore'];
      var c = nObj['counter'];
      scr = scr*c;
      scr = scr + score;
      var avg = scr / (c + 1);
      c++;
      ref.off("value");
      exitBool = true;
      ref.child(flightNum).child(name).set({
        experience: experience,
        keywords: keywords,
        score: score
      }, function(error) {
        exitBool = true;
      });
      var fref = ref.child(flightNum);
       fref.update({
         avgScore: avg,
         counter: c
       });
    }
  }
  if (!exists) {
    exitBool = true;
      ref.child(flightNum).set({
        [name] : {
          experience: experience,
          keywords: keywords,
          score: score
        },
        avgScore: score,
        counter: 1
      }, function(error) {
        exitBool = true;
      });
  }
}, function (errorObject) {
  console.log("The read failed: " + errorObject.code);
});

if(exitBool) {
  process.exit();
}
