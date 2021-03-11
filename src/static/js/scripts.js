// Default base url for axios
// axios.defaults.baseURL = "http://localhost:8000";

// Accept cookies without third party
$(".without-third-party").on("click", function () {
  Cookies.set("googleanalytics", false);
});

// // Open and close the sidebar on medium and small screens
// function w3_open() {
//   document.getElementById("mySidebar").style.display = "block";
//   document.getElementById("myOverlay").style.display = "block";
//   if(window.innerWidth > 992) {

//    }
// }
var sideBar = $("#mySidebar");
function w3_close() {
  sideBar.hide("slide", { direction: "right" }, 400);
  sideBar.removeClass("showSideBar");
  if (window.innerWidth > 992) {
  }
}

// Burger menu button toggle
$("#sidenav-toggle").on("click", function () {
  var sideBar = $("#mySidebar");
  if (sideBar.hasClass("showSideBar")) {
    sideBar.hide("slide", { direction: "right" }, 400);
    sideBar.removeClass("showSideBar");
  } else {
    sideBar.show();
    sideBar.addClass("showSideBar");
  }
});

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
// $("html").addClass("hide-overflow");
// $(window).on("load", function () {
//   $("html").removeClass("hide-overflow");
//   $("#overlay").fadeOut(500);
// });

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
setInterval(function () {
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
        sessionStorage.setItem("country", data.data.country_name);
        sessionStorage.setItem("continent", data.data.time_zone.split("/")[0]);
        if (questionsNearYouWrapper.length > 0) {
          loadNearYouQuestions();
        }
      })
      .catch((err) => {
        console.error(err.status);
      });
  }
}, 3000);

if (questionsNearYouWrapper.length > 0) {
  loadNearYouQuestions();
}

var countryInput = $("#id_country");
var continentInput = $("#id_continent");
var registerForm = $("#raykomfi-register-form");
var signinForm = $("#signin-form");
var registerWithNoSignUpForm = $("#register-with-no-sign-up-form");
function createCookie(name, value, days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    var expires = "; expires=" + date.toGMTString();
  } else var expires = "";
  document.cookie = name + "=" + value + expires + "; path=/";
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

  if (
    registerWithNoSignUpForm[0] &&
    sessionStorage.getItem("continent") == "Europe"
  ) {
    var len = registerWithNoSignUpForm[0].length;
    for (var i = 0; i < len; ++i) {
      registerWithNoSignUpForm[0][i].readOnly = true;
    }
    registerWithNoSignUpForm.append(
      '<p class="red white-text center">لا يسمح بالزوار من الإتحاد الأوروبي بالتسجيل في المنصة</p>'
    );
  }

  if (sessionStorage.getItem("continent") == "Europe") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++)
      if (cookies[i].split("=")[0].trim() !== "csrftoken") {
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
            var message = `<a href='${item.description}'>لديك رأي جديد على إستفسارك ${item.target} من ${item.actor}<div class='w3-tiny w3-margin-top'>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "reply") {
            var message = `<a href='${item.description}'>لديك رد جديد على رأيك من ${item.actor}<div class='w3-tiny'>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "message") {
            var message = `<a href='${item.description}'>لديك رسالة جديدة من ${item.actor}<div class='w3-tiny w3-margin-top'>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "report") {
            var message = `<a href='${item.description}'>لديك بلاغ جديد<div class='w3-tiny w3-margin-top'>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "post_accepted") {
            var message = `<a href='${item.description}'>تم قبول إستفسارك ${item.target}<div class='w3-tiny w3-margin-top'>${item.timestamp}</div></a>`;
            return "<li class='w3-display-container'>" + message + "</li>";
          }

          if (item.verb === "best_user") {
            var message = `<a href='${item.description}'> مبروك لقد دخلت ترتيب أفضل أعضاء الشهر الماضي <i class="fa fa-star raykomfi-gold" aria-hidden="true"></i>
            <div class='w3-tiny w3-margin-top'>${item.timestamp}</div></a>`;
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

// User area dropdown
$(".dropbtn-user-area").on("click", function () {
  $("#loggedin-user-area-dropdown").toggleClass("raykomfi-show");
});

// Force Raykomfi in the beginning
var postCreateTitle = $("#create-post-form #id_title");
var postEditTitle = $("#edit-post-form #id_title");
var postCreateNoRegistrationTitle = $(
  "#create-post-with-no-registration-form #id_title"
);

if (
  postCreateTitle.length > 0 ||
  postEditTitle.length > 0 ||
  postCreateNoRegistrationTitle.length > 0
) {
  var postTitle = postCreateTitle.length > 0 ? postCreateTitle : false;
  if (postTitle === false) {
    postTitle = postEditTitle.length > 0 ? postEditTitle : false;
  }
  if (postTitle === false) {
    postTitle =
      postCreateNoRegistrationTitle.length > 0
        ? postCreateNoRegistrationTitle
        : false;
  }

  if (postTitle !== false) {
    postTitle.on("keyup", (e) => {
      var val = postTitle.val();
      if (
        val.indexOf("https") > 0 ||
        val.indexOf("http") > 0 ||
        val.indexOf(".com") > 0 ||
        val.indexOf("www") > 0
      ) {
        postTitle.val("رايكم في ");
        errorAlert("لا يمكنك إضافة رابط في عنوان الموضوع");
      }
    });

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
  if (window.location.hash.indexOf("to") > 0) {
    var showHideRepliesBtn = $(
      $(anchor.parent().parent()[0]).find(".show-hide-replies-bar")[0]
    );

    $("html,body").animate(
      { scrollTop: anchor.parent().parent().offset().top - 250 },
      "slow"
    );
    setTimeout(() => {
      showHideRepliesBtn.click();
      anchor
        .parent()
        .parent()
        .stop()
        .animate({ backgroundColor: "#FFFFE0" }, 250)
        .animate({ backgroundColor: "#FFFFFF" }, 250)
        .animate({ backgroundColor: "#FFFFE0" }, 250)
        .animate({ backgroundColor: "#FFFFFF" }, 250)
        .animate({ backgroundColor: "#FFFFE0" }, 250)
        .animate({ backgroundColor: "#FFFFFF" }, 250);
    }, 700);
  } else {
    $("html,body").animate({ scrollTop: anchor.offset().top - 150 }, "slow");
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

M.AutoInit();

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

var toStripLinkTags = /(<([^>]+)>)/gi;

// Edit comment
$(document).on("click", ".edit-comment-btn", (e) => {
  var commentContent = e.target.dataset.content.replace(toStripLinkTags, "");
  var commentId = e.target.dataset.commentId;
  var closestEditCommentForm = $(".edit-comment-btn")
    .parent()
    .find(".editCommentForm-" + commentId);
  closestEditCommentForm[0][1].value = commentContent;
  closestEditCommentForm.css("display", "block");
  closestEditCommentForm.parent().find(".comment").hide();
  closestEditCommentForm.parent().find(".comment-action-btn").hide();
  $(closestEditCommentForm[0][1]).focus();
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
  var replyContent = e.target.dataset.content.replace(toStripLinkTags, "");
  var replyId = e.target.dataset.replyId;
  var closestEditReplyForm = $(".edit-reply-btn")
    .parent()
    .find(".editReplyForm-" + replyId);
  closestEditReplyForm[0][1].value = replyContent;
  closestEditReplyForm.css("display", "block");
  closestEditReplyForm.parent().find(".reply").hide();
  closestEditReplyForm.parent().find(".reply-action-btn").hide();
  $(closestEditReplyForm[0][1]).focus();
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

// Toggle comment without registration
$("#add-comment-no-register, .top-add-comment").on("click", () => {
  $(".commentNoRegisterForm").toggleClass("raykomfi-display-block");
  $(".signed-in-comment").toggleClass("raykomfi-display-block");
});

tinymce.init({
  selector: ".post-content",
  plugins: "advlist lists link charmap preview hr anchor pagebreak",
  toolbar_mode: "floating",
  max_height: 400,
  toolbar: [
    "undo redo | bold italic | styleselect | alignleft aligncenter alignright alignjustify | bullist numlist link preview",
  ],
  autoresize: false,
  height: 500,
  min_height: 400,
  menubar: false,
  directionality: "rtl",
  language: "ar",
  preview_styles: true,
});

// // Post keywords generation
// var postKeywordsWrapper = $('.post-keywords')
// var keywords = postKeywordsWrapper.data().keywords.split(',')
// if(postKeywordsWrapper && keywords) {
//   var generatedTags = ''
//   for(var i = 0; i < keywords.length; i++){
//     generatedTags += ` <span class="w3-padding raykomfi-main-background-color">${keywords[i]}</span>`
//   }

//   postKeywordsWrapper.html(generatedTags)
// }

// Question as anonymous
$("#anonymous-question-btn").on("click", function () {
  $("#page-to-add-question").hide();
  $("#add-question-no-register").show();
});

// Set anonymous image
$("#anonymous-image").attr("src", $("#id_creator_image").val());

// Show hide replies
$(document).on("click", ".show-hide-replies-bar", function () {
  $(this).parent().prev().toggleClass("raykomfi-show");
  if ($(this).parent().prev().hasClass("raykomfi-show")) {
    $(this).text("أخفي الردود");
  } else {
    $(this).text("أظهر الردود");
  }
});

// Initialize aos animation
AOS.init();

if ($("#typed-strings").length > 0) {
  // Initialize typed js
  var options = {
    stringsElement: "#typed-strings",
    typeSpeed: 40,
  };

  var typed = new Typed(".for-typed-js", options);
}

$(".top-add-comment").on("click", function () {
  $(".commentNoRegisterForm").addClass("raykomfi-display-block");
  $(".signed-in-comment").addClass("raykomfi-display-block");
  setTimeout(function () {
    $("html, body").animate(
      {
        scrollTop: $(".add-comment-section").offset().top,
      },
      1000
    );
  }, 100);
});

// Category Dropdown
$(".category-button").on("click", function () {
  var categoryWrapper = $(".category-wrapper");
  if (categoryWrapper.hasClass("show-category")) {
    categoryWrapper.removeClass("show-category");
    categoryWrapper.hide("slide", { direction: "up" }, 300);
  } else {
    categoryWrapper.addClass("show-category");
    categoryWrapper.show("slide", { direction: "up" }, 300);
  }
});

// Set report comment or reply url
$(document).on("click", ".raykomfi-report-btn", function () {
  var data = $(this).data();

  if (data.hasOwnProperty("replyUrl")) {
    $("#reply-reported-url").val(data.replyUrl);
    $("#reportReply").show();
  } else {
    $("#comment-reported-url").val(data.commentUrl);
    $("#reportComment").show();
  }
});

// Change notification circle colour when footer is reached
$(window).scroll(function () {
  var hT = $("#footer").offset().top,
    hH = $("#footer").outerHeight(),
    wH = $(window).height(),
    wS = $(this).scrollTop(),
    scrollTop = $(window).scrollTop();
  if (scrollTop >= 0 && scrollTop < $("footer").offset().top - 1200) {
    $("#goto-bottom").show();
    $("#goto-bottom").css({
      color: "#3498db",
    });
  } else {
    $("#goto-bottom").hide();
  }

  if (wS > hT + hH - wH - 120) {
    $(".noti-dropbtn").css({
      backgroundColor: "#FFFFFF",
      color: "#3498db",
    });
    $("#goto-top").show();
    $("#goto-top").css({
      color: "#FFFFFF",
    });
  } else {
    $(".noti-dropbtn").css({
      color: "#FFFFFF",
      backgroundColor: "#3498db",
    });

    $("#goto-top").hide();
  }
});

// Scroll to top and down
$("#goto-top").on("click", function () {
  $("html, body").animate({ scrollTop: 0 }, "slow");
});
$("#goto-bottom").on("click", function () {
  $("html, body").animate({ scrollTop: $("footer").offset().top }, "slow");
});

// Truncate comment
var comment = $(".comment");
comment.each(function (count, comment) {
  var commentJq = $(comment);
  var commentContentWrapper = $($(comment).children()[0]);
  if (commentJq.height() > 150) {
    commentContentWrapper.addClass("raykomfi-truncate");
  }
});

$(document).on("click", ".comment", function () {
  var theClickedCommentShowMore = $($(this).children(0)[0]);

  if (theClickedCommentShowMore.hasClass("raykomfi-truncate")) {
    theClickedCommentShowMore.removeClass("raykomfi-truncate");
  }
});

// Email not active btn
$("#email-not-active-btn").on("click", function () {
  infoAlert(
    'فعل بريدك الإلكتروني أولا, يمكنك طلب رابط التفعيل مرة أخرى من <a href="/user/send-link/">هنا</a>'
  );
});
