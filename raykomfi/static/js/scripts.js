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

var $searchLoading = $("#spinner").hide();
$(document)
  .ajaxStart(function () {
    $searchLoading.show();
  })
  .ajaxStop(function () {
    $searchLoading.hide();
  });

// New message preview
$("#new-message-content").on("keyup", (e) => {
  let content = e.target.value;
  let converter = new showdown.Converter();
  content = converter.makeHtml(content);
  $("#message-preview").html(content);
});

// Lazy load images
$(".lazy-img").Lazy({
  scrollDirection: "vertical",
  effect: "fadeIn",
  visibleOnly: true,
  effectTime: 1000,
});

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
          if (item.verb === "comment") {
            var message = `<a href='${item.description}'>لديك تعليق جديد على منشورك ${item.target} من ${item.actor}<div>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "reply") {
            var message = `<a href='${item.description}'>لديك رد جديد على تعليقك من ${item.actor}<div>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "message") {
            var message = `<a href='${item.description}'>لديك رسالة جديدة من ${item.actor}<div>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }
        })
        .join("");

      for (var i = 0; i < menus.length; i++) {
        menus[i].innerHTML = messages;
      }
    } else {
      menus[0].innerHTML = "<div class=''>لا يوجد لديك إشعارات حاليا</div>";
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

/* When the user clicks notification button, 
toggle between hiding and showing the dropdown content */
function show_hide_notifications() {
  document.getElementById("noti-dropdown").classList.toggle("noti-show");
}

$("#noti-btn").on("click", () => {
  show_hide_notifications();
});

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
  if (!event.target.matches(".noti-dropbtn")) {
    var dropdowns = document.getElementsByClassName("noti-dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("noti-show")) {
        openDropdown.classList.remove("noti-show");
      }
    }
  }
};

// Show search field
$("#search-btn").on("click", () => {
  $("#search-field-wrapper").toggleClass("show-search-field");
});

// Edit created display time
fixTime();

// Force Raykomfi in the beginning
let postTitle = $("#create-post-form #id_title");
if (postTitle.length > 0) {
  if (postTitle.val().length < 1) {
    postTitle.val("رايكم في ");
    postTitle.on("keydown", (e) => {
      let currentVal = e.target.value;
      if (currentVal.length <= 9) {
        e.target.value = "رايكم في ";
      }

      let count = (currentVal.match(/رايكم في/g) || []).length;
      if (count > 1) {
        postTitle.val("رايكم في");
      }
    });
  }
}

// Get best user of the month
let bestUserWrapper = $("#user-of-the-month");
let whereToDisplayResponse = $("#display-best-user");
let bestUserLoading = $("#sk-chase-best-user");
bestUserLoading.css("display", "block");
if (bestUserWrapper) {
  axios({
    method: "GET",
    url: "/api/best-users/",
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      let name = response.data[0].username;
      let agreed = response.data[0].my_comments__votes__sum;
      let id = response.data[0].id;
      let displayHtml = `<a href="/user/profile/${id}/"><strong>${name}</strong></a> بـ <span> <span
      class="agreed-number">${agreed}</span> عضو متفق مع
  آرائه</span>`;

      whereToDisplayResponse.html(displayHtml);
      bestUserLoading.css("display", "none");
    })
    .catch((err) => {
      bestUserWrapper.hide();
    });
}
