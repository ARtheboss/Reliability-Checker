function parseURLParams() {
    var url = window.location.href;
    var queryStart = url.indexOf("?") + 1,
        queryEnd   = url.indexOf("#") + 1 || url.length + 1,
        query = url.slice(queryStart, queryEnd - 1),
        pairs = query.replace(/\+/g, " ").split("&"),
        parms = {}, i, n, v, nv;

    if (query === url || query === "") return;

    for (i = 0; i < pairs.length; i++) {
        nv = pairs[i].split("=", 2);
        n = decodeURIComponent(nv[0]);
        v = decodeURIComponent(nv[1]);

        if (!parms.hasOwnProperty(n)) parms[n] = [];
        parms[n].push(nv.length === 2 ? v : null);
    }
    return parms;
}

/*function httpGet(uri,alias,command,content){
  //console.log("hello 1");
  var xmlHttp = new XMLHttpRequest();
  var params = "alias="+alias+"&action="+command;
  if (content != null) {
      params = params + "&content="+content;
  }
  var url = "http://"+uri+"?"+params;
  xmlHttp.open("GET", url, false);
  xmlHttp.send(null);
  return xmlHttp.responseText;
  var returnedText = xmlHttp.responseText;z
  //console.log("hello 2");
}*/

function getJSONfile(url){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            result(xhttp.responseText);
        }
    };

    xhttp.open("GET", url, true);
    xhttp.send();
}

var search = parseURLParams()['search'];
getJSONfile("http://3.14.29.188:5000/get_info?url=" + search);

function result(text){
  document.getElementById('loading').style.display = 'none';
  text = JSON.parse(text)



  document.getElementById('main').innerHTML = search
  document.getElementById('bias').innerHTML = text[0]['bias']
  document.getElementById('country').innerHTML = text[0]['country']
  document.getElementById('date').innerHTML = text[0]['date'].substr(0,10)
  document.getElementById('lastUpdated').innerHTML = text[0]["last_updated"].substr(0,10)
  document.getElementById('links').innerHTML = text[0]["links"]
  document.getElementById('pressFreedom').innerHTML = text[0]["press_freedom"]+"th"
  document.getElementById('ranking').innerHTML = text[0]["ranking"]+"th"
  document.getElementById('reporting').innerHTML = text[0]["reporting"]

  var last_entry = Date.parse(text[0]['date']);
  var last_updated = Date.parse(text[0]["last_updated"]);

  var score = 0
  if (text[0]["links"]>50000){
    score += 2.5
  }else if(text[0]["links"]>=30000){
    score += 1.5
  }else{
    score += 0.5
  }

  if (text[0]["ranking"] < 1000){
    score += 1.5
  }else if(text[0]["ranking"] < 100000){
    score += 1
  }else if(text[0]["ranking"] < 1000000){
    score += 0.5
  }

  if (text[0]["reporting"]=="very high"){
    score += 5
  }else if (text[0]["reporting"]=="high"){
    score += ((5/6) * 5)
  }else if (text[0]["reporting"]=="mostly factual"){
    score += ((5/6) * 4)
  }else if(text[0]["reporting"]=="mixed"){
    score += ((5/6) * 3)
  }else if(text[0]["reporting"]=="low"){
    score += ((5/6) * 2)
  }else{
    score += (5/6)
  }

  if (text[0]["bias"]=="center"){
    score+=2.5
  }else if((text[0]["bias"]=="left-center") || (text[0]["bias"]=="right-center")){
    score += 2
  }else if((text[0]["bias"]=="left") || (text[0]["bias"]=="right")){
    score += 1
  }else{
    score += 0.5
  }

  if (text[0]["press_freedom"] < 50){
    score += 2
  }else if(text[0]["press_freedom"] <= 80){
    score += 1
  }else if(text[0]["press_freedom"] <= 120){
    score += 0.5
  }

  if(last_entry-last_updated < 5){
    score += 1.5
  }else if(last_entry-last_updated < 30){
    score += 1
  }
  score = score * (2/3)
  document.getElementById('score').innerHTML = Math.round(score*100)/100 + "/10";
  document.getElementById('score2').innerHTML = Math.round(score*100)/100 + "/10";
  document.getElementById('score').style.color = "rgb("+(256-score**2*256/100).toString()+","+(score**2*256/100).toString()+",0)";

  var i;
  var totalStars = 0;
  for (i = 0; i < text[1].length; i++) {
    var div = document.createElement("div");
    div.style.width = "750px";
    div.style.height = "35";
    div.style.color = "black";
    div.innerHTML = text[1][i]["review"] + ":" + text[1][i]["username"] + " gave " + text[1][i]["stars"] + "stars";
    //document.getElementById("reviews").appendChild(div);
    totalStars += text[1][i]["stars"]
  }
  document.getElementById('userAverage').innerHTML = (totalStars / (text[1].length)).toString() + "/5";


}
