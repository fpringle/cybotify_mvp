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
  const data = plotData.map(pd => {
    const r = fields.map(f => pd[f]);
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
  $('#spiderPlot').empty();
  Plotly.newPlot('spiderPlot', data, layout);
};

const setName = (name) => {
  $('#playlistName').empty();
  $('#playlistName').append($('<span/>').text(name));
};

let playlistFeatures;

const fillList = (trackData) => {
  $('#trackContainer').empty();
  trackData.forEach(track => {
    const p = $('<p/>').addClass('trackInfo').html(`${track.name}<br>${track.artists}`);
    p.attr('id', 'track' + track.id);
    $('#trackContainer').append(p);
  });
};

$(document).ready(() => {
  const url = JSON.parse($('#ws_url').text());
  const socket = new WebSocket('ws://' + window.location.host + url);
  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data?.features) {
      // final stage
      playlistFeatures = data.features;
      plotSpider(data.features);
      console.log(data.track_features);
      data.track_features.forEach(track => {
        const elem = $('#track' + track.id);
        const hoverOn = (e) => {
          plotSpider(playlistFeatures, track);
        };
        const hoverOff = (e) => {
          plotSpider(playlistFeatures);
        };
        console.log("hover")
        elem.hover(hoverOn, hoverOff);
      });
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
