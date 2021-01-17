function successAlert(message) {
    $.toast({
        text: message,
        textAlign: "center",
        hideAfter: 2000,
        bgColor: "#4caf50",
        textColor: "#ffffff",
        position : 'top-center',
        showHideTransition : 'slide',
        allowToastClose: false,
        loader: false,
        icon: 'success',
        stack: 3
      });
}

function errorAlert(message) {
    $.toast({
        text: message,
        textAlign: "center",
        hideAfter: 2000,
        bgColor: "#f44336",
        textColor: "#ffffff",
        position : 'top-center',
        showHideTransition : 'slide',
        allowToastClose: false,
        loader: false,
        icon: 'error',
        stack: 3
      });
}

function infoAlert(message) {
    $.toast({
        text: message,
        textAlign: "center",
        hideAfter: 2000,
        bgColor: "#616161",
        textColor: "#ffffff",
        position : 'top-center',
        showHideTransition : 'slide',
        allowToastClose: false,
        loader: false,
        icon: 'info',
        stack: 3
      });
}