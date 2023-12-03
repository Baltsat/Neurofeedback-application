document.addEventListener("DOMContentLoaded", function () {
    let startTime;
    let intervalId;

    function startChrono() {
        startTime = new Date().getTime();
        intervalId = setInterval(updateChrono, 1000);
    }

    function updateChrono() {
        const currentTime = new Date().getTime();
        const elapsedTime = currentTime - startTime;

        const hours = Math.floor(elapsedTime / 3600000);
        const minutes = Math.floor((elapsedTime % 3600000) / 60000);
        const seconds = Math.floor((elapsedTime % 60000) / 1000);

        document.getElementById("chrono").innerText = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    }

    function pad(value) {
        return value < 10 ? `0${value}` : value;
    }

    // Ajout de la fonction startChrono au niveau global pour qu'elle puisse être appelée depuis le bouton
    window.startChrono = startChrono;
});

document.addEventListener("DOMContentLoaded", function () {
  var sizeRange = document.getElementById("sizeRange");
  var colorRange = document.getElementById("colorRange");
  var firepit = document.querySelector(".firepit");

//position
/*positionSlider.addEventListener("input", function () {
      firepit.style.width = this.value + "px";
      firepit.style.height = this.value + "px";
  });*/

  sizeRange.addEventListener('input', function() {
      const newSize = this.value;
      firepit.style.transform = `scale(${newSize})`;
  });

  colorRange.addEventListener("input", function () {
      // Modifier la couleur de l'élément en fonction de la valeur du curseur de couleur
      var hue = this.value; // La valeur est entre 0 et 360
      firepit.style.filter = "hue-rotate(" + hue + "deg)";
  });
});
