function generateStars() {
  let opinionPower = $(".opinion-power");
  let starsGenerated = "";
  if (opinionPower.length > 0) {
    for (let i = 0; i < opinionPower.length; i++) {
      if(opinionPower[i].innerHTML.indexOf('span') > 0) {
        opinionPower[i].innerHTML = opinionPower[i].innerHTML
        continue;
      }
      let opinionPowerValue =
        parseFloat(opinionPower[i].innerHTML.replace(",", ".")) || false;
      starsGenerated = "";
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
          '<span><i class="fa fa-star-o" aria-hidden="true"></i></span>';
      }

      opinionPower[i].innerHTML = starsGenerated;
    }
  }
}
