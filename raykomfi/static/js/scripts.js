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
    var options = {
        inDuration: 0,
        outDuration: 0
    };
    var instances = M.Materialbox.init(elems, options);
});

var mouseDirection = null

function detectMouseWheelDirection(e) {
    var delta = null,
        direction = false;
    if (!e) { // if the event is not provided, we get it from the window object
        e = window.event;
    }
    if (e.wheelDelta) { // will work in most cases
        delta = e.wheelDelta / 60;
    } else if (e.detail) { // fallback for Firefox
        delta = -e.detail / 2;
    }
    if (delta !== null) {
        direction = delta > 0 ? 'up' : 'down';
    }

    return direction;
}

document.onmousewheel = function (e) {
    mouseDirection = detectMouseWheelDirection(e);
};

if (window.addEventListener) {
    document.addEventListener('DOMMouseScroll', function (e) {
        mouseDirection = detectMouseWheelDirection(e);
    });
}

window.onscroll = function (e) {
    myFunction(e)
};


var navbar = document.getElementById("navbar");
var sticky = navbar.offsetTop;
var mainParagrah = document.getElementById('main-paragraph');
var raykomfiLogo = document.getElementById('raykomfi-logo')

function myFunction(e) {
    var scrollDirection = detectMouseWheelDirection(e);

    if (window.pageYOffset > sticky) {
        navbar.classList.add("sticky")
    } else {
        navbar.classList.remove("sticky");
    }
}