function generateStars() {
  let opinionPower = $(".opinion-power");
  let starsGenerated = "";
  if (opinionPower.length > 0) {
    for (let i = 0; i < opinionPower.length; i++) {
      let opinionPowerValue = parseFloat(opinionPower[i].innerHTML.replace(",", ".")) || false;
      starsGenerated = "";
      console.log(opinionPowerValue)
      if (opinionPowerValue) {
        for (let i = 0; i < parseInt(opinionPowerValue); i++) {
          starsGenerated +=
            '<span><i class="fa fa-star"aria-hidden="true"></i></span>';
        }

        if (opinionPowerValue % 1 > 0.0) {
          starsGenerated +=
            '<span><i class="fa fa-star-half-o" aria-hidden="true"></i></span>';
        }
      } else {
        starsGenerated =
         opinionPower[i].innerHTML;
      }

      opinionPower[i].innerHTML = starsGenerated;
    }
  }
}
