const addComment = new Vue({
  delimiters: ["[[", "]]"],
  el: "#comment",
  data: {
    comment_content: null,
    post_id: parseInt(document.getElementById("post_id").value),
    success_msg: "",
    err_msg: "",
  },
  methods: {
    submitForm: function () {
      axios({
        method: "POST",
        url: "/api/comment/add", //django path name
        headers: {
          "X-CSRFTOKEN": Cookies.get("csrftoken"),
          "Content-Type": "application/json",
        },
        data: { content: this.comment_content, post_id: this.post_id }, //data
      })
        .then((response) => {
          let view_html = response.data.view;
          console.log(view_html);
          let post_wrapper = document.getElementById("posts-wrapper");
          post_wrapper.innerHTML = view_html;
        })
        .catch((err) => {
          console.log(err.message);
        });
    },
  },
});
