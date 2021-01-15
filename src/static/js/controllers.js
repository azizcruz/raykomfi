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
  if (content) {
    $(this)[0][2].disabled = true;
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
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
        }
      });
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
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
        var comment_id = response.data.comment_id
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
      })
      .catch((err) => {
        $(this)[0][2].disabled = false;
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
        }
      });
  }
});

// Add comment no registration
$(document).on("submit", "form.commentNoRegisterForm", function (e) {
  e.preventDefault();
  let content = replacePlainLinks(e.target[1].value);
  let profile_image = "/" + e.target[2].value;
  let { postId } = e.target.dataset;
  if (content && profile_image) {
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
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
        }

        if (err.response.status === 400) {
          $("#noRegisterCommentError").html(err.response.data.message);
          setTimeout(() => {
            $("#noRegisterCommentError").html("");
          }, 1500);
        }
      });
  } else {
    custom_alert("يوجد خطأ من المستخدم, حدث الصفحة وأعد المحاولة", "");
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
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
        } else if (
          err.response.status === 403 &&
          err.response.data.detail === "لم يتم تزويد بيانات الدخول."
        ) {
          custom_alert(
            "<a href='/user/signin/'>سجل دخولك</a> أو <a href='/user/register/'>سجل في المنصة</a> للمشاركة",
            ""
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
          sendBtn.attr("disabled", false);
          sendBtn.text("إرسال");
        }, 60 * 1000);
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
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
        custom_alert(
          "محاولات متكررة, يرجى المحاولة لاحقا",
          "<i class='fa fa-warning'></i>"
        );
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
          custom_alert(
            "محاولات متكررة, يرجى المحاولة لاحقا",
            "<i class='fa fa-warning'></i>"
          );
        }
      });
  }
});


var latestCommentWrapper = $('#latest-comments-wrapper');
var similarQuestionsWrapper = $('.similar-questions-wrapper');
var ajaxLoading = $('.ajax-loading-request-wrapper');
// Latest Comments Load
function loadLatestComments() {
  ajaxLoading.show(1000);
  axios({
    method: "GET",
    url: "/api/comment/latest-comments"
  })
    .then((response) => {
      ajaxLoading.hide(1000);
      latestCommentWrapper.html(response.data.view)
    })
    .catch((err) => {
      theBtn.addClass("admin-action-btn");
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        custom_alert(
          "محاولات متكررة, يرجى المحاولة لاحقا",
          "<i class='fa fa-warning'></i>"
        );
      } else {
        ajaxLoading.hide('clip', 200)
        latestCommentWrapper.appendChild('<div class="no-results-now-style">لا توجد نتائج حاليا</div>')
      }
    });
}

function loadSimilarQuestions() {
  ajaxLoading.show(1000);
  axios({
    method: "POST",
    url: "/api/post/similar-posts",
    data: {
      category: $('#post-category').val()
    },
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      ajaxLoading.hide(1000);
      console.log(response.data.view)
      similarQuestionsWrapper.html(response.data.view)
    })
    .catch((err) => {
      theBtn.addClass("admin-action-btn");
      if (
        err.response.status === 403 &&
        err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
      ) {
        custom_alert(
          "محاولات متكررة, يرجى المحاولة لاحقا",
          "<i class='fa fa-warning'></i>"
        );
      } else {
        ajaxLoading.hide('clip', 200)
        latestCommentWrapper.appendChild('<div class="no-results-now-style">لا توجد نتائج حاليا</div>')
      }
    });
}


if(latestCommentWrapper.length > 0) {
  loadLatestComments()
  setInterval(function() {
    loadLatestComments()
  }, 30000)
}

if(similarQuestionsWrapper.length > 0) {
  loadSimilarQuestions()
}