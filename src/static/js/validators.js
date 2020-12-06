var formToValidate = $(
  "#raykomfi-register-form, #profile-form, #signin-form, #forgot-password-form, #create-post-form, #edit-post-form, #forgot-no-register-code, #change-password-form, #change-email-form, #new-message-form, #requestActivationLinkForm, #failedActivationForm, #register-with-no-sign-up-form, #create-post-with-no-registration-form"
);

if (formToValidate.length > 0) {
  formToValidate.parsley().on("field:validated", function (e) {});
}
