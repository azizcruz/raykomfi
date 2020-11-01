function generateStars() {
  let opinionPower = $(".opinion-power");
  if (opinionPower.length > 0) {
    for (let i = 0; i < opinionPower.length; i++) {
      let opinionPowerValue =
        parseFloat(opinionPower[i].innerHTML.replace(",", ".")) || false;
      let starsGenerated = "";
      if (opinionPowerValue) {
        for (let i = 0; i < parseInt(opinionPowerValue); i++) {
          starsGenerated +=
            '<span><i class="fa fa-star"aria-hidden="true"></i></span>';
        }

        if (opinionPowerValue % 1 > 0.0) {
          starsGenerated +=
            '<span><i class="fa fa-star-half-o" aria-hidden="true"></i></span>';
        }

        opinionPower[i].innerHTML = starsGenerated;
      }
    }
  }
}
