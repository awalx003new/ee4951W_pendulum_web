function showLoad(){
    var paragraph = document.getElementById("running");
    var text = document.createTextNode("Running Test, Please wait for Results");
    paragraph.appendChild(text);

    var div = document.getElementById("upload");
    if (div.style.display !== 'none') {
        div.style.display = 'none';
    }
}

/*
function toggleAbout(){
    var x = document.getElementById("about");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}
*/

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

/*
  function actuate() {
    //print(<h4>Hello!<h4>)

    fetch('${window.origin}/test',{
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache: "no-cache",
      headers: new Headers({
        "content-type": "application/json"
      })
    })

    .then(function (response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function(data) {
        console.log(data);
      });
    })

    .catch(function(error) {
      console.log("Fetch error: " + error);
    });
*/


/*For hamburger menu (triple bar icon) */
/* Toggle between showing and hiding the navigation menu links when the user clicks on the hamburger menu / bar icon */
/*
function myFunction() {
  var x = document.getElementById("myLinks");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
*/
