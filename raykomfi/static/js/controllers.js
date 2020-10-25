let post_wrapper = $("#posts-wrapper");
let message_view = $("#messages-view");
let view_html = "";
let loading = $("#spinner");

function custom_alert(message, icon) {
  Swal.fire({
    title: "",
    html: message,
    icon: icon,
    showCloseButton: false,
    showConfirmButton: false,
    showCancelButton: true,
    focusConfirm: false,
    cancelButtonText: "إغلاق",
    cancelButtonAriaLabel: "Thumbs down",
  });
}

// Add reply
$(document).on("submit", "form.replyForm", function (e) {
  e.preventDefault();
  let content = e.target[0].value;
  let { commentId } = e.target.dataset;
  if (content) {
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
        let comment_view = $(`#comment-id-${commentId}`);
        view_html = response.data.view;
        comment_view.html(view_html);
        fixTime();
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "<h3>محاولات متكررة, يرجى المحاولة لاحقا</h3>",
            "warning"
          );
        }
      });
  }
});

// Add comment
$(document).on("submit", "form.commentForm", function (e) {
  e.preventDefault();
  let content = e.target[0].value;
  let { postId } = e.target.dataset;
  if (content) {
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
        let view_html = response.data.view;
        let post_wrapper = document.getElementById("posts-wrapper");
        post_wrapper.innerHTML = view_html;
        $("#lazyLoadLinkComments").hide();
        fixTime();
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "<h3>محاولات متكررة, يرجى المحاولة لاحقا</h3>",
            "warning"
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
        fixTime();
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "<h3>محاولات متكررة, يرجى المحاولة لاحقا</h3>",
            "warning"
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
        fixTime();
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "<h3>محاولات متكررة, يرجى المحاولة لاحقا</h3>",
            "warning"
          );
        }
      });
  }
});

// Posts search
$(document).on("submit", "form.postsSearchForm", function (e) {
  e.preventDefault();
  let link = $(this);
  let q = link.serializeArray()[0].value;
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
        view_html = response.data.view;
        message_view.html(view_html);
        $(document).ready(() => {
          console.log(response.data);
          let view_html = response.data.view;
          console.log(view_html);
          let post_wrapper = document.getElementById("raykomfi-posts");
          $("#lazyLoadLink").css("display", "none");
          loading.css("display", "none");
          post_wrapper.innerHTML = view_html;
          fixTime();
        });
      })
      .catch((err) => {
        if (
          err.response.status === 403 &&
          err.response.data.detail === "ليس لديك صلاحية للقيام بهذا الإجراء."
        ) {
          custom_alert(
            "<h3>محاولات متكررة, يرجى المحاولة لاحقا</h3>",
            "warning"
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
