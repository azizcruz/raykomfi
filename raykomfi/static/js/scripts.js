// For sidenav
document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.sidenav');
    var options = {
        edge: 'right'
    };
    var instances = M.Sidenav.init(elems, options);
});

// For category dropdown
document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.dropdown-trigger');
    var options = {
        alignment: 'right'
    };
    var instances = M.Dropdown.init(elems, options);
});

document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var options = {};
    var instances = M.FormSelect.init(elems, options);
});

document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.materialboxed');
    var options = {};
    var instances = M.Materialbox.init(elems, options);
});