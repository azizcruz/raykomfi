// Get best user of the month
let bestUserWrapper = $("#user-of-the-month");
let whereToDisplayResponse = $("#display-best-users ol");
let bestUserLoading = $("#sk-chase-best-user");
bestUserLoading.css("display", "block");
let displayHtml = "";
if (bestUserWrapper) {
  axios({
    method: "GET",
    url: "/api/best-users/",
    headers: {
      "X-CSRFTOKEN": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      let users = response.data;
      if (users.length > 0) {
        for (let i = 0; i < users.length; i++) {
          let user = users[i];
          displayHtml += `<li><a href="/user/profile/${user.id}/"><strong>${user.username}</strong></a> بـ <span> <span
        class="agreed-number">${user.my_comments__votes__sum}</span> عضو متفق مع
    آرائه</span> </li>`;
        }
      } else {
        displayHtml = `<p class="center">لم يتم إختيار الأعضاء بعد </p>`;
      }

      whereToDisplayResponse.html(displayHtml);
      bestUserLoading.css("display", "none");
    })
    .catch((err) => {
      bestUserWrapper.hide();
    });
}
document.addEventListener("DOMContentLoaded", function () {
  var elems = document.querySelectorAll(".collapsible");
  var options = {};
  var instances = M.Collapsible.init(elems, options);
});
