var performance_config = {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    },
    {
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 1
    },
    {
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

scatter_config = {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: [],
            fill: false,
            showLine: false,
            pointBackgroundColor: 'rgba(54, 162, 235, 0.3)',

        }]
    },
    options: {
        scales: {
            xAxes: [{
                type: 'linear',
                position: 'bottom',
                scaleLabel: {
                  display: true,
                  labelString: 'Prediction'
                }
            }],
            yAxes: [{
                type: 'linear',
                position: 'left',
                scaleLabel: {
                  display: true,
                  labelString: 'Actual'
                }
            }]
        },
        legend: {
          display: false
        }
    }
}

jQuery(document).ready(function(){

  $("#data-analytics-view").hide();
  $("#machine-learning-view").hide();

  $("#data-overview-button").click(function(){
    $('#data-overview-button').css('color', '#346cb0');
    $('#data-overview-button').css('background-color', '#f4f4f4');
    $('#data-analytics-button').css('color', '#f4f4f4');
    $('#data-analytics-button').css('background-color', '#346cb0');
    $('#machine-learning-button').css('color', '#f4f4f4');
    $('#machine-learning-button').css('background-color', '#346cb0');
    $("#data-analytics-view").hide();
    $("#machine-learning-view").hide();
    $("#data-overview-view").show();
  });

  $("#data-analytics-button").click(function(){
    $('#data-analytics-button').css('color', '#346cb0');
    $('#data-analytics-button').css('background-color', '#f4f4f4');
    $('#data-overview-button').css('color', '#f4f4f4');
    $('#data-overview-button').css('background-color', '#346cb0');
    $('#machine-learning-button').css('color', '#f4f4f4');
    $('#machine-learning-button').css('background-color', '#346cb0');
    $("#data-overview-view").hide();
    $("#machine-learning-view").hide();
    $("#data-analytics-view").show();
  });

  $("#machine-learning-button").click(function(){
    $('#machine-learning-button').css('color', '#346cb0');
    $('#machine-learning-button').css('background-color', '#f4f4f4');
    $('#data-overview-button').css('color', '#f4f4f4');
    $('#data-overview-button').css('background-color', '#346cb0');
    $('#data-analytics-button').css('color', '#f4f4f4');
    $('#data-analytics-button').css('background-color', '#346cb0');
    $("#data-overview-view").hide();
    $("#data-analytics-view").hide();
    $("#machine-learning-view").show();
  });
});

async function start(id, host) {
  const response = await fetch(host + '/column/' + id, {
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

async function fetch_models(id, host) {

  // Get model information using Django REST API
  const modelResponse = await fetch(host + '/model/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  const modelJson = await modelResponse.json();

  // Get model information using Django REST API
  const projectResponse = await fetch(host + '/projects/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  const projectJson = await projectResponse.json();

  var models = ['svm', 'rf']
  if (modelJson[0]['accuracy'] == 0 && modelJson[0]['f1'] == 0 && modelJson[0]['roc'] == 0) {
    performance_config['data']['datasets'].pop();
    var metrics = ['explained_variance', 'r2'];
    var names = ['Explained Variance Score', 'R2 Score'];
  } else {
    var metrics = ['accuracy', 'f1', 'roc'];
    var names = ['Accuracy Score', 'F1 Score', 'AUC-ROC Score'];
  }

  // Iterate over each model and get their respective accuracy, f1 and roc score
  for (var i = 0; i < modelJson.length; i++){
    var obj = modelJson[i];
    performance_config['data']['labels'].push(obj['name']);
    var colors = ['54, 162, 235', '60, 186, 159', '196, 88, 80']

    for (var j = 0; j < metrics.length; j++){
      performance_config['data']['datasets'][j]['label'] = names[j];
      performance_config['data']['datasets'][j]['data'].push(obj[metrics[j]]);
      performance_config['data']['datasets'][j]['backgroundColor'].push('rgba(' + colors[j] + ', 0.3)');
      performance_config['data']['datasets'][j]['borderColor'].push('rgba(' + colors[j] + ', 1)');
    }

    params = JSON.parse(obj['params'].replace(/'/g, '"'));
    for (key in params) {
      document.getElementById(models[i] + '-' + key).innerHTML = key + ': ' + params[key];
    }

    document.getElementById(models[i] + '-fit_time').innerHTML = 'Train Runtime: ' + obj['fit_time'] + 's';
    document.getElementById(models[i] + '-score_time').innerHTML = 'Test Runtime: ' + obj['score_time'] + 's';
    document.getElementById(models[i] + '-model_size').innerHTML = 'Model Size: ' + obj['model_size'] + 'KB';

    if (obj['confusion'] != 0){

      var labels = JSON.parse(projectJson[0]['columns'].replace(/'/g, '"'));
      var bottom_tr = document.createElement("TR");
      var left_tr = document.createElement("TR");

      matrix = JSON.parse(obj['confusion']);
      for (var j = 0; j < matrix.length; ++j) {
        var tr = document.createElement("TR");
        for (var k = 0; k < matrix[j].length; ++k) {
          var td = document.createElement("TD");
          var text = document.createTextNode(matrix[j][k]);
          td.appendChild(text)
          tr.appendChild(td)
        }
        document.getElementById(models[i] + "-confusion").appendChild(tr);

        var bottom_td = document.createElement("TD");
        var left_td = document.createElement("TD");
        var bottom_text = document.createTextNode(labels[j]);
        var left_text = document.createTextNode(labels[j]);
        bottom_td.appendChild(bottom_text)
        bottom_tr.appendChild(bottom_td)
        left_td.appendChild(left_text)
        left_tr.appendChild(left_td)
      }
      document.getElementById(models[i] + "-confusion-bottom").appendChild(bottom_tr);
      document.getElementById(models[i] + "-confusion-left").appendChild(left_tr);
    }

    else {
      scatter_config['data']['datasets']['data'] = [];
      errors = JSON.parse(obj['errors']);
      for (var j = 0; j < errors.length; ++j){
        var actual = errors[j][0];
        var predicted = errors[j][1];
        scatter_config['data']['datasets'][0]['data'].push({x: predicted, y: actual});
      }
      var context = document.getElementById(models[i] + "-error-chart");
      var chart = new Chart(context, scatter_config);
      console.log(chart);

      /*
      var bottom_tr = document.createElement("TR");
      var left_tr = document.createElement("TR");
      var bottom_td = document.createElement("TD");
      var left_td = document.createElement("TD");
      var bottom_text = document.createTextNode('Predicted');
      var left_text = document.createTextNode('Actual');
      bottom_td.appendChild(bottom_text)
      bottom_tr.appendChild(bottom_td)
      left_td.appendChild(left_text)
      left_tr.appendChild(left_td)

      document.getElementById(models[i] + "-confusion-bottom").appendChild(bottom_tr);
      document.getElementById(models[i] + "-confusion-left").appendChild(left_tr);
      */
    }
  }

  const columnResponse = await fetch(host + '/column/' + id, {
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
