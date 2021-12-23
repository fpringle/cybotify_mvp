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
  $('#spiderPlot').empty();
  Plotly.newPlot('spiderPlot', data, layout);
};

const setName = (name) => {
  $('#playlistName').empty();
  $('#playlistName').append($('<span/>').text(name));
};

let playlist_features;
let track_features;

const fillList = (trackData) => {
  $('#trackContainer').empty();
  trackData.forEach(track => {
    const artists = track.artists.join(', ');
    const p = $('<p/>').addClass('trackInfo').html(`${track.name}<br>${artists}`);
    p.attr('id', 'track' + track.id);
    $('#trackContainer').append(p);
  });
};

$(document).ready(() => {
  const getPlaylistFeatures = fetch(playlistUrl, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => {
    return response.json();
  }).then(playlist => {
    setName(playlist.name);
    fillList(playlist.tracks);
  });

  const getTrackInfo = fetch(analysisUrl, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => {
    return response.text();
  }).then(text => {
    return JSON.parse(text);
  }).then(features => {
    playlist_features = features.features;
    plotSpider(playlist_features);
    track_features = features.track_features;
  });

  Promise.all([getPlaylistFeatures, getTrackInfo]).then(() => {
    track_features.forEach(track => {
      const id = track.id;
      const elem = $('#track' + id);
      const hoverOn = (e) => {
        plotSpider(playlist_features, track);
      };
      const hoverOff = (e) => {
        plotSpider(playlist_features);
      };
      elem.hover(hoverOn, hoverOff);
    });
  });
});

})();
