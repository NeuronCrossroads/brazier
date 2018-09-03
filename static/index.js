var chart_ids = ['metric1-canvas','metric2-canvas','metric3-canvas','metric4-canvas']
var charts = []

for (var chart_id in chart_ids) {
  var ctx = document.getElementById(chart_ids[chart_id]).getContext('2d');
  var chart = new Chart(ctx, {
      // The type of chart we want to create
      type: 'line',

      // The data for our dataset
      data: {
          labels: [],
          datasets: [{
              backgroundColor: 'rgba(0,0,0,0)',
              borderColor: '#ffa000',
              pointRadius: 0,
              data: [],
          }]
      },

      // Configuration options go here
      options: {
        legend: {
          display: false
        },
        events: []
      }
  });
  charts.push(chart)
}

function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();
}

function removeData(chart) {
    chart.data.labels.pop();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.pop();
    });
    chart.update();
}
