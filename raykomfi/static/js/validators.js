$(
  "#raykomfi-register-form, #profile-form, #signin-form, #forgot-password-form, #create-post-form, #change-password-form"
)
  .parsley()
  .on("field:validated", function (e) {
    console.log(this);
  });
