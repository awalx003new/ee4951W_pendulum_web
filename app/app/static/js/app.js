function showLoad(){
    var paragraph = document.getElementById("running");
    var text = document.createTextNode("Running Test, Please wait for Results");
    paragraph.appendChild(text);

    var div = document.getElementById("upload");
    if (div.style.display !== 'none') {
        div.style.display = 'none';
    }
}

// For dynamic progress bar for file upload
function update() {
  var element = document.getElementById("myBar");
  var width = 1;
  // Every 5 milliseconds, the function scene() will be called
  var identity = setInterval(scene, 5);
  function scene() {
    if (width >= 100) {
      clearInterval(identity);
    } else {
      width++;
      element.style.width = width + '%';
    }
  }
}


