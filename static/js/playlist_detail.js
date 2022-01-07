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
let track_elements;
let track_data;
let fuse;

const makeElements = (trackData) => {
  track_elements = [];
  trackData.forEach(track => {
    const artists = track.artists.join(', ');
    const p = $('<p/>').addClass('trackInfo').html(`${track.name}<br>${artists}`);
    p.attr('id', 'track' + track.id);
    track_elements.push(p);
  });
};

const linkHover = () => {
  track_features.forEach(track => {
    const id = track.id;
    const elem = $('#track' + id);
    if (elem.length === 0) return;

    const hoverOn = (e) => {
      plotSpider(playlist_features, track);
    };
    const hoverOff = (e) => {
      plotSpider(playlist_features);
    };
    elem.hover(hoverOn, hoverOff);
  });
};

const fillList = (indices) => {
  $('#trackContainer').empty();
  if (!indices) {
    track_elements.forEach(elem => {
      $('#trackContainer').append(elem);
    });
  } else {
    indices.forEach(idx => {
      $('#trackContainer').append(track_elements[idx]);
    });
  }
};

const filter = (text) => {
  return text ? fuse.search(text).map(result => result.refIndex) : track_data.map((e,i) => i);
};

const updateFilter = (searchBox) => {
  const curVal = searchBox.val();
  fillList(filter(curVal));
  linkHover();
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
    makeElements(playlist.tracks);
    track_data = playlist.tracks;
    fuse = new Fuse(track_data, {
      threshold: 0.4,
      keys: [
        'name',
        'artists',
//        'album',
      ],
    });
    fillList();
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
    linkHover();
    updateFilter(searchBox);
  });

  const searchBox = $('#searchBoxInput');
  document.getElementById('searchBoxInput').addEventListener('input', event => {
    if (searchBox.val() == '') $('#clearSearchInput').hide();
    else $('#clearSearchInput').show();
    updateFilter(searchBox);
  });

  $('#clearSearchInput').click(() => {
    searchBox.val('');
    $('#clearSearchInput').hide();
    updateFilter(searchBox);
  });

  $('#clearSearchInput').hide();
  //searchBox.focus();
});

})();
