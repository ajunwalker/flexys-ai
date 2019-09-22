function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

async function start(id) {

  var finishedAnalytics = false;

  while (finishedAnalytics == false){
    const response = await fetch('http://0.0.0.0:8000/projects/' + id, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    const myJson = await response.json();
    finishedAnalytics = myJson[0]['analytics_complete']
  }

  if (finishedAnalytics == true){
    document.getElementById("analyze-label").classList.remove("status-text-selected");
    document.getElementById("generate-label").classList.add("status-text-selected");
  }

  var finishedModels = false;
  while (finishedModels == false){
    const response = await fetch('http://0.0.0.0:8000/projects/' + id, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    const myJson = await response.json();
    finishedModels = myJson[0]['models_complete']

    if (finishedModels == true){
      window.location = 'http://0.0.0.0:8000/project/' + id;
    }
  }

}

window.onload = function () {
}
