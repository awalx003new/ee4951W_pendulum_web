function showLoad(){
    var paragraph = document.getElementById("running");
    var text = document.createTextNode("Running Test, Please wait for Results");
    paragraph.appendChild(text);

    var div = document.getElementById("upload");
    if (div.style.display !== 'none') {
        div.style.display = 'none';
    }
}

function toggleAbout(){
    var x = document.getElementById("about");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}