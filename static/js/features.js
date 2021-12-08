(function() {
const plotSpider = (plotData) => {
  const fields = [
    'acousticness',
    'danceability',
    'energy',
    'instrumentalness',
//    'key',
    'liveness',
//    'loudness',
//    'mode',
    'speechiness',
//    'tempo',
//    'time_signature',
    'valence',
  ];
  const theta = fields.map(f => f[0].toUpperCase() + f.substr(1).toLowerCase());
  const r = fields.map(f => plotData[f]);
  const data = [{
    type: 'scatterpolar',
    //mode: 'lines+markers',
    hovertemplate: '<i>%{theta}</i>: %{r:.3f}',
    hoverinfo: 'none',
    r,
    theta,
    fill: 'toself',
  }];
  const layout = {
    polar: {
      radialaxis: {
        visible: true,
        range: [0, 1]
      },
  //    bgcolor: '#A9A9A9',
    },
    showlegend: false,
    font: {
      size: 20,
    },
    //paper_bgcolor: '#A9A9A9',
  };
  Plotly.newPlot('spiderPlot', data, layout);
};

$(document).ready(() => {
  const features = JSON.parse($('#features').text());
  const values = features.features;
  plotSpider(values);
});

})();
