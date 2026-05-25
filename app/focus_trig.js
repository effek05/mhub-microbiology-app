let timerInterval;

const countdownDisplay = document.getElementById("countdownDisplay");
const nutriText = document.getElementById("nutri-counter");

countdownDisplay.textContent = "00:00";


// Get the root element

// Create a function for setting a variable value

function myFunction_set(nv) {
  var r = document.querySelector(':root');
  // Set the value of variable --primary-bg-color to another value (in this case "green")
  var ol = getComputedStyle(r).getPropertyValue('--nutrients-now')
  r.style.setProperty('--nutrients-now', ol + nv);
};



function startTimer() {
  const minutes = parseInt(document.getElementById("minutesInput").value);

  if (isNaN(minutes) || minutes <= 0) {
    alert("Please enter a valid number of minutes.");

    return;
  }

  let timeRemaining = minutes * 60;

  updateDisplay(timeRemaining);

  clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    timeRemaining--;

    ;
    myFunction_set(updateDisplay(timeRemaining));

    if (timeRemaining <= 0) {
      clearInterval(timerInterval);

      alert("⏰Time's up!");
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
  return nutri;
}