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

const setName = (name) => {
  $('#playlistName').empty();
  $('#playlistName').append($('<span/>').text(name));
};

const fillList = (trackData) => {
  $('#trackContainer').empty();
  trackData.forEach(track => {
    const p = $('<p/>').addClass('trackInfo').html(`${track.name}<br>${track.artists}`);
    $('#trackContainer').append(p);
  });
};

$(document).ready(() => {

  const emptyData = {
    acousticness: 0,
    danceability: 0,
    energy: 0,
    instrumentalness: 0,
    liveness: 0,
    speechiness: 0,
    valence: 0
  };
  plotSpider(emptyData);

  const url = JSON.parse($('#ws_url').text());
  const socket = new WebSocket('ws://' + window.location.host + url);
  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data?.features) {
      // final stage
      plotSpider(data.features);
    } else if (data?.tracks) {
      // second stage
      fillList(data.tracks);
    } else if (data?.name) {
      // first stage
      setName(data.name);
    }
  };
});

})();
