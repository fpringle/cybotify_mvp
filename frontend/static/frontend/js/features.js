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
    r,
    theta,
    fill: 'toself',
  }];
  const layout = {
    polar: {
      radialaxis: {
        visible: true,
        range: [0, 1]
      }
    },
    showlegend: false
  };
  Plotly.newPlot('spiderPlot', data, layout);
};

$(document).ready(() => {
  console.log($('#features').text());
  const features = JSON.parse($('#features').text());
  const values = features.features;
  plotSpider(values);
});
