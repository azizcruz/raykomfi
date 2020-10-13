function addReply(e) {
  e.preventDefault();
  console.log(e);
}

let post_wrapper = $("#posts-wrapper");
let message_view = $("#messages-view");
let view_html = "";

// Add reply
$(document).on("submit", "form.replyForm", function (e) {
  e.preventDefault();
  let content = e.target[0].value;
  let { postId, commentId } = e.target.dataset;
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
        post_id: parseInt(postId),
        comment_id: parseInt(commentId),
      },
    })
      .then((response) => {
        view_html = response.data.view;
        post_wrapper.html(view_html);
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
