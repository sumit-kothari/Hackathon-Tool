function competitionFormSubmitted() {

    var competition_submit_button = document.getElementById('competition_submit_button');    
    competition_submit_button.disabled = true;
    
    var competition_submission_loader = document.getElementById('competition_submission_loader');    
    competition_submission_loader.style.display = "block";
}

var dialog = document.querySelector('#join_team_dialog');
var showModalButton = document.querySelector('#join_team');

if (dialog && showModalButton) {
    if (!dialog.showModal) {
        dialogPolyfill.registerDialog(dialog);
    }
    showModalButton.addEventListener('click', function () {
        dialog.showModal();
    });
    dialog.querySelector('.close').addEventListener('click', function () {
        dialog.close();
    });
}

function blockBrowser() {
    var allowedBrowers = ['Firefox', 'Chrome']

    var parser = new UAParser();

    var browserName = parser.getResult().browser.name;


    if(allowedBrowers.indexOf(browserName) < 0)
    {  
        console.log("This website is best viewed in Chrome or Firefox browser");

        // document.write("This website is best viewed in Chrome or Firefox browser");
        document.getElementsByTagName('body')[0].innerHTML = "<h3>Please visit this website in Google Chrome or Firefox browser</h3>"
    } else {
    	document.getElementById('blockBrowserErrorDiv').style.display = "none";
    }

    console.log('good browser')
}

blockBrowser()

function setBgColor() {
    var dialog1 = document.querySelector('#index_page');
    var dialog2 = document.querySelector('#about-us-page');

    var body_element = document.querySelector('.mdl-layout__content');

    if (dialog1 || dialog2) {
        body_element.style.background = "linear-gradient(rgba(217, 218, 239, 0.35), rgba(32, 32, 183, 0.5))";
    } else {
        body_element.style.background = "#fff";
    }
}

setBgColor()