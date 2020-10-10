function addReply(e) {
  e.preventDefault();
  console.log(e);
}

let post_wrapper = $("#posts-wrapper");
let view_html = "";

$(document).on("submit", "form.replyForm", function (e) {
  console.log(this.children);
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
