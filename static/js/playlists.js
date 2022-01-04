(function() {

const playlistListElem = (data) => {
  const name = $('<span/>').addClass('playlistName');
  name.text(data.name || 'Untitled');
  const updated = $('<span/>').addClass('playlistLastUpdated');
  updated.text(`last updated ${data.last_updated}`);
  const div = $('<div/>').addClass("playlist").append(name).append(updated)
  const a = $('<a/>').attr('href', detailUrl + data.id).append(div);
  return $('<li/>').append(a);
};

const fillList = ({data, sortBy, filterBy}) => {
  const list = $('#playlistList')
  list.empty();

  let _data = data.slice()

  if (filterBy && filterBy !== 'ALL') {
    _data = _data.filter(d => d.status === filterBy);
  }

  if (sortBy) {
    if (sortBy === 'Default') {
    } else if (sortBy === 'Alphabetical') {
      const makeUntitled = name => name || 'Untitled';
      _data.sort((a, b) => makeUntitled(a.name) < makeUntitled(b.name) ? -1 : 1);
    } else {
      throw new Error('unknown sort type: ' + type);
    }
  }

  _data.forEach(d => list.append(playlistListElem(d)));
};

let currentFilter = "ALL";
let currentSort = "Default";

$(document).ready(() => {
  let playlists;
  fetch(requestUrl, {
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => {
    return response.json();
  }).then(playlists => {
    fillList({
      data: playlists,
      filterBy: $('#filter').val(),
    });

    $('#filter').change(function() {
      const newFilter = $(this).val();
      if (newFilter === currentFilter) return;
      currentFilter = newFilter;
      fillList({
        data: playlists,
        filterBy: newFilter,
      });
    });
  });

  $('#sort').change(function() {
    const newSort = $(this).val();
    if (newSort === currentSort) return;
    currentSort = newSort;
    fillList({
      data: playlists,
      filterBy: currentFilter,
      sortBy: newSort,
    });
  });
});
})();
