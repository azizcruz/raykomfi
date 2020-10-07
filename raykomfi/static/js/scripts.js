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
  myFunction();
};

// A CSRF token is required when making post requests in Django
// To be used for making AJAX requests in script.js
window.CSRF_TOKEN = document.getElementById("csrf_token").innerHTML;

function myFunction() {
  if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
    document
      .getElementById("myTop")
      .classList.add("w3-card-4", "w3-animate-opacity");
    document.getElementById("myIntro").classList.add("w3-show-inline-block");
  } else {
    document.getElementById("myIntro").classList.remove("w3-show-inline-block");
    document
      .getElementById("myTop")
      .classList.remove("w3-card-4", "w3-animate-opacity");
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

// Smooth scroll to hash
$(function () {
  $("html, body").animate(
    {
      scrollTop: $(window.location.hash).offset().top,
    },
    1000
  );
  return false;
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
