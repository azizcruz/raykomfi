(function ($) {
  // Load more posts
  $("#lazyLoadLink").on("click", function () {
    var link = $(this);
    var page = link.data("page");
    $.ajax({
      type: "post",
      url: "/api/lazy-posts/",
      data: {
        page: page,
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
  });

  // Load more comments
  $("#lazyLoadLinkComments").on("click", function () {
    var link = $(this);
    var page = link.data("page");
    $.ajax({
      type: "post",
      url: "/api/lazy-comments/",
      data: {
        page: page,
        post_id: parseInt(document.getElementById("post_id").value),
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
        $("#posts-wrapper").append(data.comments_html);
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
})(jQuery);
