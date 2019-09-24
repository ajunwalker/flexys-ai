function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

async function start(id, host) {

  var finishedAnalytics = false;

  while (finishedAnalytics == false){

    wait(2000);

    const response = await fetch(host + '/projects/' + id, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    const myJson = await response.json();
    finishedAnalytics = myJson[0]['analytics_complete']

    if (finishedAnalytics == true){
      document.getElementById("analyze-label").classList.remove("status-text-selected");
      document.getElementById("generate-label").classList.add("status-text-selected");
    }
  }

  var finishedModels = false;
  while (finishedModels == false){

    wait(2000);

    const response = await fetch(host + '/projects/' + id, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    const myJson = await response.json();
    finishedModels = myJson[0]['models_complete']

    if (finishedModels == true){
      window.location = host + '/project/' + id;
    }
  }

}

window.onload = function () {
}
