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

const fillList = (data) => {
  const list = $('#playlistList')
  list.empty();
  data.forEach(d => list.append(playlistListElem(d)));
};

const sortBy = (data, type) => {
  if (type == 'Default') return data;
  else if (type == 'Alphabetical') {
    const sortedData = data.slice();
    return sortedData.sort((a, b) => a.name < b.name ? -1 : 1);
  } else {
    throw new Error('unknown sort type: ' + type);
  }
};

const filterByStatus = (data, status) => {
  if (status !== "ALL") data = data.filter(d => d.status == status);
  fillList(data);
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
  }).then(response => {
    playlists = response;
    console.log(playlists);
    filterByStatus(playlists, $('#filter').val());

    $('#filter').change(function() {
      const newFilter = $(this).val();
      if (newFilter === currentFilter) return;
      currentFilter = newFilter;
      filterByStatus(playlists, newFilter);
    });
  });

  $('#sort').change(function() {
    const newSort = $(this).val();
    if (newSort === currentSort) return;
    currentSort = newSort;
    filterByStatus(sortBy(playlists, newSort), currentFilter);
  });
});
})();
