let post_wrapper = $("#posts-wrapper");
let message_view = $("#messages-view");
let view_html = "";
let loading = $("#spinner");

function custom_alert(message, icon) {
  $("#alert-message").html(message);
  document.getElementById("alert-icon").innerHTML = icon;
  document.getElementById("alert-modal").style.display = "block";
}

// Add reply
$(document).on("submit", "form.replyForm", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let { commentId } = e.target.dataset;
  var button = $(this)[0][2];
  if (content) {
    $(this)[0][2].disabled = true;

    // Reply as anonymous
    if ($(button).data().hasOwnProperty("asAnonymous")) {
      axios({
        method: "POST",
        url: "/api/reply/add/anonymous",
        headers: {
          "X-CSRFTOKEN": Cookies.get("csrftoken"),
          "Content-Type": "application/json",
        },
        data: {
          content: content,
          comment_id: parseInt(commentId),
        },
      })
        .then((response) => {
          $(this)[0][2].disabled = false;
          let comment_view = $(`#comment-id-${commentId}`);
          var showMore = $($($(comment_view.parent().children()[0]).children()[2]).children()[0])
          view_html = response.data.view;
          comment_view.html(view_html);
          generateStars();
          e.target[0].value = "";
          successAlert("تم إضافة ردك");
        })
        .catch((err) => {
          $(this)[0][2].disabled = false;
          if (
            err.response.status === 403 &&
            err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
          ) {
            errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
          } else {
            errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
          }
        });
    } else {
      axios({
        method: "POST",
        url: "/api/reply/add",
        headers: {
          "X-CSRFTOKEN": Cookies.get("csrftoken"),
          "Content-Type": "application/json",
        },
        data: {
          content: content,
          comment_id: parseInt(commentId),
        },
      })
        .then((response) => {
          $(this)[0][2].disabled = false;
          let comment_view = $(`#comment-id-${commentId}`);
          view_html = response.data.view;
          comment_view.html(view_html);
          generateStars();
          e.target[0].value = "";
          successAlert("تم إضافة ردك");
        })
        .catch((err) => {
          $(this)[0][2].disabled = false;
          if (
            err.response.status === 403 &&
            err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
          ) {
            errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
          } else {
            errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
          }
        });
    }
  }
});

// Edit reply
$(document).on("submit", "form.closest-edit-reply-form", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let { replyId, commentId } = e.target.dataset;
  if (content) {
    axios({
      method: "PUT",
      url: "/api/reply/edit",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: { content: content, reply_id: replyId, comment_id: commentId },
    })
      .then((response) => {
        let view_html = response.data.view;
        let comment_wrapper = document.getElementById(
          `comment-id-${commentId}`
        );
        comment_wrapper.innerHTML = view_html;
        e.target[1].value = "";
        generateStars();
        successAlert("تم تعديل ردك");
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Add comment
$(document).on("submit", "form.commentForm", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let { postId } = e.target.dataset;
  if (content) {
    $(this)[0][2].disabled = true;
    axios({
      method: "POST",
      url: "/api/comment/add",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: { content: content, post_id: postId },
    })
      .then((response) => {
        $(this)[0][2].disabled = false;
        let view_html = response.data.view;
        let post_wrapper = document.getElementById("posts-wrapper");
        var comment_id = response.data.comment_id;
        post_wrapper.innerHTML = view_html;
        $("#lazyLoadLinkComments").hide();
        e.target[1].value = "";
        generateStars();
        setTimeout(function () {
          $("html, body").animate(
            {
              scrollTop: $("#comment-id-" + comment_id).offset().top - 500,
            },
            500
          );
        }, 100);

        setTimeout(() => {
          $("#comment-id-" + comment_id)
            .stop()
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250)
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250)
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250);
        }, 700);

        successAlert("تم إضافة رأيك");
      })
      .catch((err) => {
        $(this)[0][2].disabled = false;
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          $(this)[0][2].disabled = false;
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Add comment no registration
$(document).on("submit", "form.commentNoRegisterForm", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let profile_image = e.target[2].value;
  let { postId } = e.target.dataset;
  if (content && profile_image) {
    $(this)[0][2].disabled = true;
    axios({
      method: "POST",
      url: "/api/comment/add/no-registeration",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: { content: content, post_id: postId, profile_image: profile_image },
    })
      .then((response) => {
        $(this)[0][2].disabled = false;
        let view_html = response.data.view;
        let post_wrapper = document.getElementById("posts-wrapper");
        var comment_id = response.data.comment_id;
        post_wrapper.innerHTML = view_html;
        $("#lazyLoadLinkComments").hide();
        e.target[1].value = "";
        generateStars();
        setTimeout(function () {
          $("html, body").animate(
            {
              scrollTop: $("#comment-id-" + comment_id).offset().top - 500,
            },
            500
          );
        }, 100);

        setTimeout(() => {
          $("#comment-id-" + comment_id)
            .stop()
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250)
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250)
            .animate({ backgroundColor: "#FFFFE0" }, 250)
            .animate({ backgroundColor: "#FFFFFF" }, 250);
        }, 700);

        successAlert("تم إضافة رأيك");
      })
      .catch((err) => {
        $(this)[0][2].disabled = false;
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ){
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  } else {
    errorAlert("يوجد خطأ من المستخدم, حدث الصفحة وأعد المحاولة");
  }
});

// Edit comment
$(document).on("submit", "form.closest-edit-comment-form", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let { commentId } = e.target.dataset;
  if (content) {
    axios({
      method: "PUT",
      url: "/api/comment/edit",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: { content: content, comment_id: commentId },
    })
      .then((response) => {
        let view_html = response.data.view;
        let comment_wrapper = document.getElementById(
          `comment-id-${commentId}`
        );
        comment_wrapper.innerHTML = view_html;
        // $("#lazyLoadLinkComments").hide();
        e.target[1].value = "";
        generateStars();
        successAlert("تم تعديل رأيك");
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Vote comment
$(document).on("submit", "form.voteForm", function (e) {
  e.preventDefault();
  let { commentId, userId, voteType } = e.target.dataset;
  if (voteType) {
    axios({
      method: "POST",
      url: "/api/comment/vote",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        comment_id: parseInt(commentId),
        user_id: parseInt(userId),
        action_type: voteType,
      },
    })
      .then((response) => {
        let votes_view = $(`#comment-${commentId}-vote-side-wrapper`);
        view_html = response.data.view;
        votes_view.html(view_html);
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else if (
          err.response.status === 403 &&
          err.response.data.detail === "لم يتم تزويد بيانات الدخول.") 
         {
          infoAlert("<a href='/user/signin/' class='alert-link'>سجل دخولك</a> أو <a href='/user/register/' class='alert-link'>سجل في المنصة</a> للمشاركة");
        }
      });
  }
});

// Get Message
$(document).on("submit", "form.getMessageForm", function (e) {
  e.preventDefault();
  let { messageId } = e.target.dataset;
  if (messageId) {
    axios({
      method: "POST",
      url: "/api/messages/get",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        message_id: parseInt(messageId),
      },
    })
      .then((response) => {
        view_html = response.data.view;
        message_view.html(view_html);
        let converter = new showdown.Converter();
        let message = document.getElementById("message-content-field");
        message.innerHTML = converter.makeHtml(message.innerHTML);
      })
      .catch((err) => {
        if (
          err.response &&
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Posts search
$(document).on("submit", "form.postsSearchForm", function (e) {
  e.preventDefault();
  let link = $(this);
  let q = link.serializeArray()[1].value;
  loading.css("display", "block");
  if (q) {
    axios({
      method: "POST",
      url: "/api/posts/search",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        searchField: q,
      },
    })
      .then((response) => {
        let view_html = response.data.view;
        let post_wrapper = document.getElementById("raykomfi-posts");
        $("#lazyLoadLink").css("display", "none");
        loading.css("display", "none");
        post_wrapper.innerHTML = view_html;
      })
      .catch((err) => {
        loading.css("display", "none");
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  } else {
    loading.css("display", "none");
    axios({
      method: "POST",
      url: "/api/posts/search",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        searchField: "",
      },
    })
      .then((response) => {
        let view_html = response.data.view;
        let post_wrapper = document.getElementById("raykomfi-posts");
        $("#lazyLoadLink").css("display", "none");
        loading.css("display", "none");
        post_wrapper.innerHTML = view_html;
      })
      .catch((err) => {
        loading.css("display", "none");
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Comments search
$(document).on("submit", "form.commentsSearchForm", function (e) {
  e.preventDefault();
  let link = $(this);
  let q = link.serializeArray()[1].value;
  loading.css("display", "block");
  if (q) {
    axios({
      method: "POST",
      url: "/api/comments/search",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        searchField: q,
      },
    })
      .then((response) => {
        view_html = response.data.view;
        message_view.html(view_html);
        $(document).ready(() => {
          let view_html = response.data.view;
          let post_wrapper = document.getElementById("user-comments");
          $("#lazyLoadLinkComments").css("display", "none");
          loading.css("display", "none");
          post_wrapper.innerHTML = view_html;
          generateStars();
        });
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  } else {
    loading.css("display", "none");
    axios({
      method: "POST",
      url: "/api/comments/search",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        searchField: "",
      },
    })
      .then((response) => {
        view_html = response.data.view;
        message_view.html(view_html);
        $(document).ready(() => {
          let view_html = response.data.view;
          let post_wrapper = document.getElementById("user-comments");
          $("#lazyLoadLinkComments").css("display", "none");
          loading.css("display", "none");
          post_wrapper.innerHTML = view_html;
          generateStars();
        });
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Upload Image
// $("#id_image").on("change", function (e) {
//   var file = e.target.files[0];
//   var fd = new FormData();
//   fd.append("image", file);
//   if (file.size > 0) {
//     axios({
//       method: "POST",
//       url: "/api/post/image",
//       headers: {
//         "X-CSRFTOKEN": Cookies.get("csrftoken"),
//         "Content-Type": "application/json",
//       },
//       data: fd,
//     })
//       .then((response) => {
//         console.log(response.data);
//       })
//       .catch((err) => {
//         console.log(err.message);
//       });
//   }
// });

// Add report
$(document).on("submit", "form.reportForm", function (e) {
  e.preventDefault();
  let content = e.target[1].value;
  let data = $(this).serializeArray();
  data = {
    content: data[1].value,
    reported_url: data[2].value,
    topic: data[3].value,
  };
  if (content) {
    axios({
      method: "POST",
      url: "/api/report/",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: data,
    })
      .then((response) => {
        let sendBtn = $(".send-report-btn");
        sendBtn.attr("disabled", true);
        sendBtn.text(response.data.message);
        $("form.reportForm").trigger("reset");
        setTimeout(() => {
          $("#reportComment").hide();
          $("#reportReply").hide();
          $("#reportPost").hide();
        }, 500);
        setTimeout(() => {
          sendBtn.attr("disabled", false);
          sendBtn.text("إرسال");
        }, 60 * 1000);

        $.toast({
          text: "تم إرسال بلاغك",
          textAlign: "center",
        });
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

// Delete Notifications
$(document).on("click", "#delete-all-notis", function (e) {
  axios({
    method: "DELETE",
    url: "/api/notifications/delete",
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      let deleteBtn = $("#delete-all-notis");
      let deleteBtnVal = deleteBtn.text();
      deleteBtn.attr("disabled", true);
      deleteBtn.text(response.data.message);
      $(".live_notify_list").html("<div>لا يوجد لديك إشعارات حاليا</div>");
      setTimeout(() => {
        deleteBtn.attr("disabled", false);
        deleteBtn.text(deleteBtnVal);
      }, 2000);
    })
    .catch((err) => {
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
      } else {
        errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
      }
    });
});

// Admin actions
$(document).on("click", ".admin-action-btn", function (e) {
  var theBtn = $(this);
  var adminActionMessage = $(".admin-action-message");
  e.preventDefault();
  var ans = confirm("هل أنت متأكد");
  if (ans) {
    let { id, requestType, action, url } = e.target.dataset;
    theBtn.removeClass("admin-action-btn");
    axios({
      method: "POST",
      url: "/api/admin/action",
      headers: {
        "X-CSRFTOKEN": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
      data: {
        id: id,
        type: requestType,
        action: action,
        url: url,
      },
    })
      .then((response) => {
        adminActionMessage.text(response.data.message);
        setTimeout(() => {
          theBtn.addClass("admin-action-btn");
          adminActionMessage.text("");
        }, 2000);
      })
      .catch((err) => {
        theBtn.addClass("admin-action-btn");
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
        } else {
          errorAlert("حدث خطأ غير متوقع, حاول لاحقا");
        }
      });
  }
});

var latestCommentWrapper = $(".latest-comments-wrapper");
var similarQuestionsWrapper = $(".similar-questions-wrapper");
var questionsNearYouWrapper = $(".questions-near-you-wrapper");
var ajaxLoading = $(".ajax-loading-request-wrapper");
var typedStrings = $("#typed-strings");
var latestCommentsAjaxLoading = $(
  ".ajax-loading-request-wrapper.latest-comments-load"
);
// Latest Comments Load
function loadLatestComments() {
  latestCommentsAjaxLoading.show(1000);
  axios({
    method: "GET",
    url: "/api/comment/latest-comments",
  })
    .then((response) => {
      latestCommentsAjaxLoading.hide(1000);
      latestCommentWrapper.html(response.data.view);
    })
    .catch((err) => {
      theBtn.addClass("admin-action-btn");
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        latestCommentsAjaxLoading.hide();
        errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
      } else {
        latestCommentsAjaxLoading.hide("clip", 200);
        latestCommentWrapper.appendChild(
          '<div class="no-results-now-style">لا توجد نتائج حاليا</div>'
        );
      }
    });
}

// Similar Questions
function loadSimilarQuestions() {
  ajaxLoading.show(1000);
  axios({
    method: "POST",
    url: "/api/post/similar-posts",
    data: {
      category: $("#post-category").val(),
    },
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      ajaxLoading.hide(1000);
      similarQuestionsWrapper.html(response.data.view);
    })
    .catch((err) => {
      theBtn.addClass("admin-action-btn");
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
      } else {
        ajaxLoading.hide("clip", 200);
        latestCommentWrapper.appendChild(
          '<div class="no-results-now-style">لا توجد نتائج حاليا</div>'
        );
      }
    });
}

// Questions Near You
function loadNearYouQuestions() {
  ajaxLoading.show(1000);
  axios({
    method: "POST",
    url: "/api/post/questions-near-you",
    data: {
      country: sessionStorage.getItem("country"),
    },
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      ajaxLoading.hide(1000);
      questionsNearYouWrapper.html(response.data.view);
    })
    .catch((err) => {
      theBtn.addClass("admin-action-btn");
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
      } else {
        ajaxLoading.hide(200);
        latestCommentWrapper.appendChild(
          '<div class="no-results-now-style">لا توجد نتائج حاليا</div>'
        );
      }
    });
}

// Categories
function loadCategoroies() {
  axios({
    method: "GET",
    url: "/api/categories",
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
    },
  })
    .then((response) => {
      $("#categories-wrapper").html(response.data.view);
    })
    .catch((err) => {
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        errorAlert("لقد تخطيت الحد المسموح من المحاولات, حاول لاحقا");
      }
    });
}

loadCategoroies();

if (latestCommentWrapper.length > 0) {
  loadLatestComments();
  setInterval(function () {
    loadLatestComments();
  }, 30000);
}

if (similarQuestionsWrapper.length > 0) {
  loadSimilarQuestions();
}

if (questionsNearYouWrapper.length > 0) {
  loadNearYouQuestions();
}
