let timerInterval;
let coun = 1; //change to 1

const countdownDisplay = document.getElementById("countdownDisplay");
const nutriText = document.getElementById("nutri-counter");

countdownDisplay.textContent = "00:00";


// Get the root element

// Create a function for setting a variable value

//function myFunction_set(nv) {
 // var r = document.querySelector(':root');
  // Set the value of variable --primary-bg-color to another value (in this case "green")
 // var ol = getComputedStyle(r).getPropertyValue('--nutrients-now')
 // r.style.setProperty('--nutrients-now', ol + nv);
//};


function rotat() {
  const minutes = parseInt(document.getElementById("minutesInput").value);
  if (isNaN(minutes) || minutes <= 0 || minutes > 180) {
    return;
  }


  var genImg = document.getElementById('genImg');
  //genImg.style.display = "none";

  //var myImg = document.getElementById('myImg');
  //var regi = document.getElementById('wrap-plate');
  //regi.style.display = "block";

  genImg.src = "static/images/plates/plate_" + coun + ".png";
  genImg.style.transform = "scale(1.5)";
  

  //myImg.style.marginTop =  "-25%";
  //myImg.style.marginLeft ="-50%";
  //myImg.style.zoom = "1.1"

  setInterval(function() {
    coun++;
    genImg.src = "static/images/plates/plate_" + coun + ".png";
  }, 60000);

}


function startTimer() {
  const minutes = parseInt(document.getElementById("minutesInput").value);

  if (isNaN(minutes) || minutes <= 0) {
    alert("Please enter a valid number of minutes.");

    return;
  }

  if (minutes > 180) {
    alert("Please enter a maximum of 180 minutes. Do not overwork yourself!");

    return;
  }

  let timeRemaining = minutes * 60;

  updateDisplay(timeRemaining);

  clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    timeRemaining--;

    ;
    updateDisplay(timeRemaining); //used to have myfunction() outside

    if (timeRemaining <= 0) {
      clearInterval(timerInterval);

      openModal();
    }
  }, 1000);
}

function updateDisplay(time) {
  const minutes = Math.floor(time / 60);
  const seconds = time % 60;
  const nutri = Math.round(-(seconds - 60)/3);


  countdownDisplay.textContent = `${minutes}:${seconds
    .toString()
    .padStart(2, "0")}`;

  nutriText.textContent = `${nutri}`;
  return //nutri;
}



function openModal() {
  const modal = 
      document.getElementById('myModal');
  const modalImg = 
      document.getElementById('modalImg');
  modal.style.display = 'block';
  modalImg.src = "static/images/abundance_over_time.png";
}

function closeModal() {
  const modal = 
      document.getElementById('myModal');
  modal.style.display = 'none';
}