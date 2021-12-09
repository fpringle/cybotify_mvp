(function() {

const playlistListElem = (data) => {
  const name = $('<span/>').addClass('playlistName');
  name.text(data.name || 'Untitled');
  const updated = $('<span/>').addClass('playlistLastUpdated');
  updated.text(`last updated ${data.last_updated}`);
  const div = $('<div/>').addClass("playlist").append(name).append(updated)
  const a = $('<a/>').attr('href', data.url).append(div);
  return $('<li/>').append(a);
};

const fillList = (data) => {
  const list = $('#playlistList')
  list.empty();
  data.forEach(d => list.append(playlistListElem(d)));
};

const filterByStatus = (data, status) => {
  console.log("filter by status = " + status);
  if (status !== "ALL") data = data.filter(d => d.status == status);
  fillList(data);
};

let currentFilter = "ALL";


$(document).ready(() => {
  const playlists = JSON.parse($('#playlists').text());

  filterByStatus(playlists, $('#filter').val());

  $('#filter').change(function() {
    const newFilter = $(this).val();
    if (newFilter === currentFilter) return;
    currentFilter = newFilter;
    filterByStatus(playlists, newFilter);
  });

});
})();
