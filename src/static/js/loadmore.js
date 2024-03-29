(function ($) {
  // Load more posts
  $("#lazyLoadLink").on("click", function () {
    var link = $(this);
    var page = link.data("page");
    var category = link.data("category") || false;
    var user_id = link.data("user") || false;
    $.ajax({
      type: "post",
      url: "/api/lazy-posts/",
      data: {
        page: page,
        category: category,
        user_id: user_id,
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
        console.error(status);
      },
    });
  });

  // Load more comments
  $("#lazyLoadLinkComments").on("click", function () {
    var link = $(this);
    var page = link.data("page");
    var user_id = link.data("user") || false;
    var viewer = link.data("viewer") || false;
    var post_id = document.getElementById("post_id")
      ? parseInt(document.getElementById("post_id").value)
      : false;
    $.ajax({
      type: "post",
      url: "/api/lazy-comments/",
      data: {
        page: page,
        post_id: post_id,
        user_id: user_id,
        viewer: viewer,
        csrfmiddlewaretoken: Cookies.get("csrftoken"), // from index.html
      },
      success: function (data) {
        // if there are still more pages to load,
        // add 1 to the "Load More Comments" link's page data attribute
        // else hide the link
        if (data.has_next) {
          link.data("page", page + 1);
        } else {
          link.hide();
        }
        if (user_id !== false) {
          // append html to the posts div
          $("#user-comments").append(data.comments_html);
        } else {
          // append html to the posts div
          $("#posts-wrapper").append(data.comments_html);
        }
        generateStars();
        // Truncate comment
        var comment = $(".comment");
        comment.each(function (count, comment) {
          var commentJq = $(comment);
          var commentContentWrapper = $($(comment).children()[0]);
          if (commentJq.height() > 150) {
            commentContentWrapper.addClass("raykomfi-truncate");
          }
        });
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
})(jQuery);
