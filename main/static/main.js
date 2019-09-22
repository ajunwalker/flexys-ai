var performance_config = {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'Accuracy Score',
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    },
    {
      label: 'F1 Score',
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    },
    {
      label: 'AUC-ROC Score',
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    },
  ]},
  options: {
    responsive: false,
    scales: {
      xAxes: [{
        ticks: {
          maxRotation: 90,
          minRotation: 0
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
}

var importance_config = {
  type: 'horizontalBar',
  data: {
    labels: [],
    datasets: [{
      label: 'Importance',
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    }]
  },
  options: {
    responsive: false,
    scales: {
      xAxes: [{
        ticks: {
          maxRotation: 90,
          minRotation: 0
        }
      }],
      xAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
}

jQuery(document).ready(function(){

  $("#machine-learning-view").hide();

  $("#data-analytics-button").click(function(){
    $('#data-analytics-button').css('color', '#346cb0');
    $('#data-analytics-button').css('background-color', '#f4f4f4');
    $('#machine-learning-button').css('color', '#f4f4f4');
    $('#machine-learning-button').css('background-color', '#346cb0');
    $("#machine-learning-view").hide();
    $("#data-analytics-view").show();
  });

  $("#machine-learning-button").click(function(){
    $('#machine-learning-button').css('color', '#346cb0');
    $('#machine-learning-button').css('background-color', '#f4f4f4');
    $('#data-analytics-button').css('color', '#f4f4f4');
    $('#data-analytics-button').css('background-color', '#346cb0');
    $("#data-analytics-view").hide();
    $("#machine-learning-view").show();
  });
});

async function start(id) {
  const response = await fetch('http://0.0.0.0:8000/column/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  const myJson = await response.json();

  for (var i = 0; i < myJson.length; i++){
    var obj = myJson[i];
    tag = "<tr>"

    if (obj["type"] == "numerical"){
      tag += '<td><strong>' + obj["name"] + "</strong></td>";
      tag += '<td style="text-align:right">' + (obj["filled"] * 100) + "%</td>";
      tag += '<td style="text-align:right">' + obj["min"] + "</td>";
      tag += '<td style="text-align:right">' + obj["mean"] + "</td>";
      tag += '<td style="text-align:right">' + obj["median"] + "</td>";
      tag += '<td style="text-align:right">' + obj["max"] + "</td>";
      $("#numerical-table tbody").append(tag + "</tr>");
    }
    else {
      tag += '<td><strong>' + obj["name"] + "</strong></td>";
      tag += '<td style="text-align:right">' + (obj["filled"] * 100) + "%</td>";
      tag += '<td style="text-align:right">' + obj["unique"] + "</td>";
      $("#categorical-table tbody").append(tag + "</tr>");
    }
  }
}

async function fetch_models(id) {

  // Get model information using Django REST API
  const modelResponse = await fetch('http://0.0.0.0:8000/model/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  const modelJson = await modelResponse.json();

  // Iterate over each model and get their respective accuracy, f1 and roc score
  for (var i = 0; i < modelJson.length; i++){
    var obj = modelJson[i];
    performance_config['data']['labels'].push(obj['name']);
    performance_config['data']['datasets'][0]['data'].push(obj['accuracy']);
    performance_config['data']['datasets'][0]['backgroundColor'].push('rgba(54, 162, 235, 0.3)');
    performance_config['data']['datasets'][0]['borderColor'].push('rgba(54, 162, 235, 1)');

    performance_config['data']['datasets'][1]['data'].push(obj['f1']);
    performance_config['data']['datasets'][1]['backgroundColor'].push('rgba(60, 186, 159, 0.3)');
    performance_config['data']['datasets'][1]['borderColor'].push('rgba(60, 186, 159, 1)');

    performance_config['data']['datasets'][2]['data'].push(obj['roc']);
    performance_config['data']['datasets'][2]['backgroundColor'].push('rgba(196, 88, 80, 0.3)');
    performance_config['data']['datasets'][2]['borderColor'].push('rgba(196, 88, 80, 1)');
  }

  const columnResponse = await fetch('http://0.0.0.0:8000/column/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  const columnJson = await columnResponse.json();

  var list = [];
  for (var i = 0; i < columnJson.length - 1; i++){
    var obj = columnJson[i];
    list.push({'name': obj['name'], 'importance': obj['importance']});
  }

  list.sort(function(a, b) {
    return ((a.importance > b.importance) ? -1 : ((a.importance == b.importance) ? 0 : 1));
  });

  for (var k = 0; k < list.length; k++) {
      if (k == 10) break;
      importance_config['data']['labels'].push(list[k].name);
      importance_config['data']['datasets'][0]['data'].push(list[k].importance);
      importance_config['data']['datasets'][0]['backgroundColor'].push('rgba(54, 162, 235, 1)');
      importance_config['data']['datasets'][0]['borderColor'].push('rgba(54, 162, 235, 1)');
  }
  load_graphs();
}

function load_graphs() {
  var ctx = document.getElementById("myChart");
  var myChart = new Chart(ctx, performance_config);

  var ctx2 = document.getElementById("importanceChart");
  var myBarChart = new Chart(ctx2, importance_config);
}

window.onload = function () {
}
