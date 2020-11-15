var formToValidate = $(
  "#raykomfi-register-form, #profile-form, #signin-form, #forgot-password-form, #create-post-form, #change-password-form, #change-email-form, #new-message-form, #requestActivationLinkForm, #failedActivationForm"
);

if (formToValidate.length > 0) {
  formToValidate.parsley().on("field:validated", function (e) {});
}
