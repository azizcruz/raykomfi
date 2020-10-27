$(
  "#raykomfi-register-form, #profile-form, #signin-form, #forgot-password-form, #create-post-form, #change-password-form, #change-email-form"
)
  .parsley()
  .on("field:validated", function (e) {});
