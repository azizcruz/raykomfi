let post_wrapper = $("#posts-wrapper");
let message_view = $("#messages-view");
let view_html = "";

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
      })
      .catch((err) => {
        console.log(err.message);
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
      })
      .catch((err) => {
        console.log(err.message);
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
        console.log(err.message);
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
        $(document).ready(() => {
          let message = document.getElementById("message-content-field");
          message.innerHTML = converter.makeHtml(message.innerHTML);
        });
      })
      .catch((err) => {
        console.log(err.message);
      });
  }
});

// Posts search
$(document).on("submit", "form.postsSearchForm", function (e) {
  e.preventDefault();
  let link = $(this);
  let q = link.serializeArray()[0].value;
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
          post_wrapper.innerHTML = view_html;
        });
      })
      .catch((err) => {
        console.log(err.message);
      });

    $.ajax({
      type: "post",
      url: "/api/lazy-posts/",
      data: {
        page: page,
        category: category,
        user_id: user_id,
        csrfmiddlewaretoken: Cookies.get("csrftoken"), // from index.html
      },
      success: function (data) {
        // if there are still more pages to load,
        // add 1 to the "Load More Posts" link's page data attribute
        // else hide the link
        if (data.has_next) {
          link.data("page", page + 1);
        } else {
          link.hide();
        }
        // append html to the posts div
        $("#raykomfi-posts").append(data.posts_html);
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
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
