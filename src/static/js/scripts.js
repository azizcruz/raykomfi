// Default base url for axios
// axios.defaults.baseURL = "http://localhost:8000";

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

var myTop = document.getElementById("myTop");
var myIntro = document.getElementById("myIntro");

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

var modal = document.getElementById("raykomfi-myModal");

// Get the image and insert it inside the modal - use its "alt" text as a caption
var img = document.getElementById("raykomfi-myImg") || false;
var modalImg = document.getElementById("raykomfi-modalImage");
var captionText = document.getElementById("raykomfi-caption");
if (img) {
  img.onclick = function () {
    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;
  };
}
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("raykomfi-close")[0];

// When the user clicks on anywhere except the image, close the modal
if (img) {
  $(document).on("click", function (event) {
    if (!$(event.target).closest("#raykomfi-myImg").length) {
      // ... clicked on the 'body', but not inside of #menutop
      modal.style.display = "none";
    }
  });
}
// When you click everywhere the image module close except when you click on the image
$("#raykomfi-modalImage").on("click", function (event) {
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
  var content = e.target.value;
  var converter = new showdown.Converter();
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
if (
  !sessionStorage.getItem("country") &&
  !sessionStorage.getItem("continent")
) {
  var options = {
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
      console.log(data);
      sessionStorage.setItem("country", data.data.country_name);
      sessionStorage.setItem("continent", data.data.time_zone.split("/")[0]);
    })
    .catch((err) => {
      console.log(err);
    });
}

var countryInput = $("#id_country");
var continentInput = $("#id_continent");
var registerForm = $("#raykomfi-register-form");
var signinForm = $("#signin-form");
function createCookie(name,value,days) {
  if (days) {
      var date = new Date();
      date.setTime(date.getTime()+(days*24*60*60*1000));
      var expires = "; expires="+date.toGMTString();
  }
  else var expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}
function eraseCookie(name) {
  createCookie(name, "", -1);
}
if (countryInput && continentInput) {
  countryInput.val(sessionStorage.getItem("country"));
  continentInput.val(sessionStorage.getItem("continent"));
  if (registerForm[0] && sessionStorage.getItem("continent") == "Europe") {
    var len = registerForm[0].length;
    for (var i = 0; i < len; ++i) {
      registerForm[0][i].readOnly = true;
    }
    registerForm.append(
      '<p class="red white-text center">لا يسمح بالزوار من الإتحاد الأوروبي بالتسجيل في المنصة</p>'
    );
  }

  if (signinForm[0] && sessionStorage.getItem("continent") == "Europe") {
    var len = signinForm[0].length;
    for (var i = 0; i < len; ++i) {
      signinForm[0][i].readOnly = true;
    }
    signinForm.append(
      '<p class="red white-text center">لا يسمح بالزوار من الإتحاد الأوروبي بالتسجيل في المنصة</p>'
    );
  }

  if (sessionStorage.getItem("continent") == "Europe") { 
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++)
    if(cookies[i].split("=")[0].trim() !== 'csrftoken') {
      eraseCookie(cookies[i].split("=")[0]);
    }
  }
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
            var message = `<a href='${
              item.description
            }'>لديك تعليق جديد على إستفسارك ${item.target} من ${
              item.actor
            }<div>${moment(item.timestamp).fromNow()}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "reply") {
            var message = `<a href='${
              item.description
            }'>لديك رد جديد على تعليقك من ${item.actor}<div>${moment(
              item.timestamp
            )
              .locale("ar-dz")
              .fromNow()}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "message") {
            var message = `<a href='${item.description}'>لديك رسالة جديدة من ${
              item.actor
            }<div>${moment(item.timestamp)
              .locale("ar-dz")
              .fromNow()}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "report") {
            var message = `<a href='${
              item.description
            }'>لديك بلاغ جديد<div>${moment(item.timestamp)
              .locale("ar-dz")
              .fromNow()}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "post_accepted") {
            var message = `<a href='${item.description}'>تم قبول إستفسارك ${
              item.target
            }<div>${moment(item.timestamp)
              .locale("ar-dz")
              .fromNow()}</div></a>`;
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

var noti_btn = $(".noti-modal");
var close_noti = $(".close-noti");

noti_btn.on("click", () => {
  $(".noti-modal__overlay").show();
});

close_noti.on("click", () => {
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

  if (!event.target.matches("#share-btn")) {
    var dropdowns = document.getElementsByClassName("raykomfi-share-dropdown");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("w3-show")) {
        openDropdown.classList.remove("w3-show");
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
var postCreateTitle = $("#create-post-form #id_title");
var postEditTitle = $("#edit-post-form #id_title");


if (postCreateTitle.length > 0 || postEditTitle.length > 0) {
  var postTitle = postCreateTitle.length > 0 ? postCreateTitle : false;
  if(postTitle === false) {
    postTitle = postEditTitle.length > 0 ? postEditTitle : false;
  }

  if(postTitle !== false) {
      postTitle.on("keydown", (e) => {
        var currentVal = e.target.value;
        if (currentVal.length <= 9) {
          e.target.value = "رايكم في ";
        }
  
        var count = (currentVal.match(/رايكم في/g) || []).length;
        if (count > 1) {
          postTitle.val("رايكم في ");
        }
      });
  }
}

// Opinion power starts algorithm
generateStars();

// Highlight of the to div box
if (window.location.hash) {
  var anchor = $(window.location.hash);
  $("html,body").animate({ scrollTop: anchor.offset().top - 50 }, "slow");
  setTimeout(() => {
    anchor
      .stop()
      .animate({ backgroundColor: "#FFFFE0" }, 250)
      .animate({ backgroundColor: "#FFFFFF" }, 250)
      .animate({ backgroundColor: "#FFFFE0" }, 250)
      .animate({ backgroundColor: "#FFFFFF" }, 250)
      .animate({ backgroundColor: "#FFFFE0" }, 250)
      .animate({ backgroundColor: "#FFFFFF" }, 250);
  }, 700);
}

// tooltip initialization
document.addEventListener("DOMContentLoaded", function () {
  var elems = document.querySelectorAll(".tooltipped");
  var options = {};
  var instances = M.Tooltip.init(elems, options);
});

// Initialize modals
document.addEventListener("DOMContentLoaded", function () {
  var elems = document.querySelectorAll(".modal");
  var options = {};
  var instances = M.Modal.init(elems, options);
});

// Share dropdown
function shareDropdown() {
  var x = document.getElementById("share-dropdown");
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
}

$("#share-btn").on("click", () => {
  shareDropdown();
});

// Copy post url
$("#copy-post-url").on("click", (e) => {
  e.preventDefault();
  var copyText = document.getElementById("inputToCopy");

  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /*For mobile devices*/

  /* Copy the text inside the text field */
  document.execCommand("copy");
});

// Cookie bar
$(".cookie-message").cookieBar({
  closeButton: ".cookie-close-button",
  expiresDays: 30,
});
$("#i-dont-want-cookies").on("click", () => {
  Cookies.set("cookiebar", "hide");
  Cookies.set("useCookies", false, { expires: 30 });
});

// Edit comment
$(document).on("click", ".edit-comment-btn", (e) => {
  var commentContent = e.target.dataset.content;
  var commentId = e.target.dataset.commentId;
  var closestEditCommentForm = $(".edit-comment-btn")
    .parent()
    .find(".editCommentForm-" + commentId);
  closestEditCommentForm[0][1].value = commentContent;
  closestEditCommentForm.css("display", "block");
  closestEditCommentForm.parent().find(".comment").hide();
  closestEditCommentForm.parent().find(".comment-action-btn").hide();
});

$(document).on("click", ".close-comment-edit-form", (e) => {
  e.preventDefault();
  var commentId = e.target.dataset.commentId;
  var closestEditCommentForm = $(".close-comment-edit-form")
    .parent()
    .parent()
    .find(".editCommentForm-" + commentId);
  closestEditCommentForm[0][1].value = "";
  closestEditCommentForm.css("display", "none");
  closestEditCommentForm.parent().find(".comment").show();
  closestEditCommentForm.parent().find(".comment-action-btn").show();
});

// Edit Reply
$(document).on("click", ".edit-reply-btn", (e) => {
  var replyContent = e.target.dataset.content;
  var replyId = e.target.dataset.replyId;
  var closestEditReplyForm = $(".edit-reply-btn")
    .parent()
    .find(".editReplyForm-" + replyId);
  closestEditReplyForm[0][1].value = replyContent;
  closestEditReplyForm.css("display", "block");
  closestEditReplyForm.parent().find(".reply").hide();
  closestEditReplyForm.parent().find(".reply-action-btn").hide();
});

$(document).on("click", ".close-reply-edit-form", (e) => {
  e.preventDefault();
  var replyId = e.target.dataset.replyId;
  var closestEditReplyForm = $(".close-reply-edit-form")
    .parent()
    .parent()
    .find(".editReplyForm-" + replyId);
  closestEditReplyForm[0][1].value = "";
  closestEditReplyForm.css("display", "none");
  closestEditReplyForm.parent().find(".reply").show();
  closestEditReplyForm.parent().find(".reply-action-btn").show();
});
