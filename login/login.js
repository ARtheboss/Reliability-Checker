String.prototype.hashCode = function() {
    var hash = 0;
    if (this.length == 0) {
        return hash;
    }
    for (var i = 0; i < this.length; i++) {
        var char = this.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

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

function signup(){
	if(document.getElementById('password').value == document.getElementById('cpassword').value){
		getJSONfile('http://3.14.29.188:5000/get_info?signup='+document.getElementById('username').value+'&hash='+document.getElementById('password').value.hashCode())
	}else{
		alert("Password don't match!")
	}
}

function login(){
	getJSONfile('http://3.14.29.188:5000/get_info?login='+document.getElementById('username').value+'&hash='+document.getElementById('password').value.hashCode())
}

function result(x){
	if(x == "1"){
		window.location.href = "../index.html";
	}else{
		alert("Incorrect Password!")
	}
}


