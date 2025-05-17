const submissionButton = document.getElementById("submission");
const userPrompt = document.getElementById("textPrompt");
const userPlay = document.getElementById("play");
const userNext = document.getElementById("next");
const userQuestion = document.getElementById("instructions");

let approvalValue = 80;
let maxApprovalValue = 100;
let houseCost = 20000; //change as necessary

userPlay.addEventListener("click", function(){
    document.getElementById("landingPage").style.display = "none";
    document.getElementById("infoPage").style.display = "block";
})

userNext.addEventListener("click", function(){
    document.getElementById("infoPage").style.display = "none";
    document.getElementById("gamePage").style.display = "block";
})

userQuestion.addEventListener("click", function(){
    document.getElementById("gamePage").style.display = "none";
    document.getElementById("infoPage").style.display = "block";
})

function changeBar(){
    const ratingBar = document.querySelector('.support');
    const percentage = (approvalValue / maxApprovalValue) * 100;

    ratingBar.style.width = `${percentage}%`;
    ratingBar.innerText = `${Math.ceil(percentage)}%`;
}

userPrompt.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        submitPrompt();
    }
});

submissionButton.addEventListener("click", function(e) {
    e.preventDefault();
    submitPrompt();
});

function submitPrompt() {
  changeBar();
  const promptText = document.getElementById("textPrompt").value;
  document.getElementById("textPrompt").value = '';

  document.getElementById("cost").innerText = "$"+houseCost;

  //testing
  document.getElementById("submittedPrompt").innerText = promptText;
}

function showLoading() {
    document.getElementById("gamePage").style.display = "none";
    document.getElementById("landingPage").style.display = "none";
    document.getElementById("infoPage").style.display = "none";
    document.getElementById("loadingPage").style.display = "block";
}    

function hideLoading() {
    document.getElementById("loadingPage").style.display = "none";
    document.getElementById("gamePage").style.display = "block";
}

// test loading
const loadScreen = document.getElementById("loadingScreen");
let isLoading = false;

loadScreen.addEventListener("click", function () {
    if (isLoading) {
        hideLoading();
    } else {
        showLoading();
    }
    isLoading = !isLoading;
});