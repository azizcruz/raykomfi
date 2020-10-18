// Default base url for axios
axios.defaults.baseURL = "http://localhost:8000";

// Open and close the sidebar on medium and small screens
function w3_open() {
  document.getElementById("mySidebar").style.display = "block";
  document.getElementById("myOverlay").style.display = "block";
}

function w3_close() {
  document.getElementById("mySidebar").style.display = "none";
  document.getElementById("myOverlay").style.display = "none";
}

// Change style of top container on scroll
window.onscroll = function () {
  if (myFunction) {
    myFunction();
  }
};

// A CSRF token is required when making post requests in Django
// To be used for making AJAX requests in script.js
window.CSRF_TOKEN = document.getElementById("csrf_token").innerHTML;

let myTop = document.getElementById("myTop");
let myIntro = document.getElementById("myIntro");

if (myTop && myIntro) {
  function myFunction() {
    if (
      document.body.scrollTop > 80 ||
      document.documentElement.scrollTop > 80
    ) {
      myTop.classList.add("w3-card-4", "w3-animate-opacity");
      myIntro.classList.add("w3-show-inline-block");
    } else {
      myIntro.classList.remove("w3-show-inline-block");
      myTop.classList.remove("w3-card-4", "w3-animate-opacity");
    }
  }
}

// Accordions
function myAccordion(id) {
  var x = document.getElementById(id);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    x.previousElementSibling.className += " raykomfi-theme";
  } else {
    x.className = x.className.replace("w3-show", "");
    x.previousElementSibling.className = x.previousElementSibling.className.replace(
      " raykomfi-theme",
      ""
    );
  }
}

var modal = document.getElementById("myModal");

// Get the image and insert it inside the modal - use its "alt" text as a caption
var img = document.getElementById("myImg") || false;
var modalImg = document.getElementById("modalImage");
var captionText = document.getElementById("caption");
if (img) {
  img.onclick = function () {
    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;
  };
}
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on anywhere except the image, close the modal
if (img) {
  $(document).on("click", function (event) {
    if (!$(event.target).closest("#myImg").length) {
      // ... clicked on the 'body', but not inside of #menutop
      modal.style.display = "none";
    }
  });
}
// When you click everywhere the image module close except when you click on the image
$("#modalImage").on("click", function (event) {
  event.stopPropagation();
});

// Page loading
$("html").addClass("hide-overflow");
$(window).on("load", function () {
  $("html").removeClass("hide-overflow");
  $("#overlay").fadeOut(500);
});

// Loading show
var $loading = $("#sk-chase").hide();
$(document)
  .ajaxStart(function () {
    $loading.show();
  })
  .ajaxStop(function () {
    $loading.hide();
  });

// New message preview
$("#new-message-content").on("keyup", (e) => {
  let content = e.target.value;
  let converter = new showdown.Converter();
  content = converter.makeHtml(content);
  $("#message-preview").html(content);
});

// Lazy load images
$(".lazy-img").Lazy();

// Get country
if (!sessionStorage.getItem("country")) {
  let options = {
    method: "GET",
    hostname: "freegeoip.app",
    port: null,
    path: "/json/",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
    },
  };
  axios
    .get("https://freegeoip.app/json/")
    .then((data) => {
      sessionStorage.setItem("country", data.data.country_name);
    })
    .catch((err) => {
      console.log(err);
    });
}

let countryInput = $("#id_country");
if (countryInput) {
  countryInput.val(sessionStorage.getItem("country"));
}

// notifications feeds
function fill_notification_badge_override(data) {
  var badges = document.getElementsByClassName("live_notify_badge_override");
  if (badges) {
    window.unreadCount = data.unread_count;
    if (data.unread_count > 0) {
      badges[0].innerHTML = '<i class="fa fa-circle" aria-hidden="true"></i>';
    } else {
      badges[0].innerHTML = "";
    }
  }
}

function fill_notification_list_override(data) {
  var menus = document.getElementsByClassName(notify_menu_class);
  if (menus) {
    if (data.unread_list.length > 0) {
      var messages = data.unread_list
        .map(function (item) {
          var message = `<a href='${item.description}'>${item.verb} من ${item.actor} <div>${item.timestamp}</div></a>`;
          return (
            "<li class='w3-display-container'>" +
            message +
            " <a class='w3-button w3-display-left'>&times;</a></li>"
          );
        })
        .join("");

      for (var i = 0; i < menus.length; i++) {
        menus[i].innerHTML = messages;
      }
    } else {
      menus[0].innerHTML =
        "<div class='w3-center'>لا يوجد لديك إشعارات حاليا</div>";
    }
  }
}

let noti_btn = $(".noti-modal");
let close_noti = $(".close-noti");

noti_btn.on("click", () => {
  $(".noti-modal__overlay").show();
});

close_noti.on("click", () => {
  console.log("shbvs");
  setTimeout(() => {
    $(".noti-modal__overlay").css("display", "none");
  }, 200);
});
