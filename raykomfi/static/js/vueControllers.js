if (window.location.href.includes("post")) {
  const addComment = new Vue({
    delimiters: ["[[", "]]"],
    el: "#comment",
    data: {
      comment_content: null,
      post_id:
        (document.getElementById("post_id") &&
          parseInt(document.getElementById("post_id").value)) ||
        null,
      success_msg: "",
      err_msg: "",
    },
    methods: {
      addComment: function () {
        if (this.post_id && this.comment_content) {
          axios({
            method: "POST",
            url: "/api/comment/add",
            headers: {
              "X-CSRFTOKEN": Cookies.get("csrftoken"),
              "Content-Type": "application/json",
            },
            data: { content: this.comment_content, post_id: this.post_id },
          })
            .then((response) => {
              let view_html = response.data.view;
              let post_wrapper = document.getElementById("posts-wrapper");
              post_wrapper.innerHTML = view_html;
              this.reset();
            })
            .catch((err) => {
              console.log(err.message);
            });
        }
      },
      reset: function () {
        this.comment_id = "";
        this.reply_content = "";
        this.comment_content = "";
        let allForms = document.querySelectorAll("form");
        for (let i = 0; i < allForms.length; i++) {
          allForms[i].reset();
        }
      },
    },
  });
}
