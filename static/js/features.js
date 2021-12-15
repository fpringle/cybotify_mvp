(function() {
const plotSpider = (...plotData) => {
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
  theta.push(theta[0]);
  const data = plotData.map(pd => {
    const r = fields.map(f => pd[f]);
    r.push(r[0]);
    return {
      type: 'scatterpolar',
      hovertemplate: '<i>%{theta}</i>: %{r:.3f}',
      hoverinfo: 'none',
      r,
      theta,
      fill: 'toself',
    };
  });
  const layout = {
    polar: {
      radialaxis: {
        visible: true,
        range: [0, 1]
      },
    },
    showlegend: false,
    font: {
      size: 20,
    },
  };
  Plotly.newPlot('spiderPlot', data, layout);
};

$(document).ready(() => {
  const features = JSON.parse($('#features').text());
  const values = features.features;
  plotSpider(values);
  const track_features = features.track_features;
  track_features.forEach(track => {
    const id = track.id;
    const elem = $('#track' + id);
    const hoverOn = (e) => {
      plotSpider(values, track);
    };
    const hoverOff = (e) => {
      plotSpider(values);
    };
    elem.hover(hoverOn, hoverOff);
  });
});

})();
