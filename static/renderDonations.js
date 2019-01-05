var showGoalStart = Date.now() - 99999;
var previousStatus = null;

function updateDonationsDisplay(status) {
    var donos = document.getElementById('donationDiv');
    var closed = document.getElementById('closedDiv');
    var custom = document.getElementById('customDiv');

    if (status.settings.mode == 'donations') {
        donos.style.display = 'block';
        closed.style.display = 'none';
        custom.style.display = 'none';

        document.getElementById('hours').innerText = status.display.hours;
        document.getElementById('donations').innerText = status.display.total;
        document.getElementById('goal').innerText = status.display.amount;

        var prog = document.getElementById('donationProgress');

        if (status.settings.showProgress) {
            prog.style.display = "block";

            var progbar = document.getElementById('donationProgressBar');
            var perc = status.display.percentage;

            if (status.donations.total > status.goal.amount) {
                perc = 100;
                progbar.classList.add('progressMaxGoal');
                progbar.classList.remove('progressNearGoal');
                progbar.classList.remove('progressNormal');
            }
            else if (perc >= 90) {
                progbar.classList.add('progressNearGoal');
                progbar.classList.remove('progressMaxGoal');
                progbar.classList.remove('progressNormal');
            }
            else {
                progbar.classList.remove('progressMaxGoal');
                progbar.classList.remove('progressNearGoal');
                progbar.classList.add('progressNormal');
            }

            progbar.style.width = perc + '%';
        }
        else {
            prog.style.display = "none";
        }
    }
    else if (status.settings.mode == 'closed') {
        donos.style.display = 'none';
        closed.style.display = 'block';
        custom.style.display = 'none';
        document.getElementById('closedDonations').innerText = status.display.total;
    }
    else if (status.settings.mode == 'custom') {
        donos.style.display = 'none';
        closed.style.display = 'none';
        custom.style.display = 'block';
        document.getElementById('customMessage').innerText = status.settings.customMessage;
    }
    else {
        donos.style.display = 'none';
        closed.style.display = 'none';
        custom.style.display = 'none';
    }
}

function updateGoalDisplay(status) {
    if (status.settings.mode == 'donations') {
        if (status.settings.showGoalAlerts && previousStatus && status.goal.goalHours > previousStatus.goal.goalHours) {
            // We blew thru a goal(s) so need to draw some attention to the fact
            // Though only for forward movement!!
            showGoalStart = Date.now();

            var goalDisplay = document.getElementById('goalText');
            var goalText = status.settings.goalMessage || "Time Extension";

            goalText = goalText.toUpperCase();
            goalDisplay.innerText = goalText;
            goalDisplay.setAttribute("data-text", goalText);
        }
    }

    var goalDisplay = document.getElementById('goalText');

    // Show goal alert
    goalDisplay.style.display = status.settings.showGoalAlerts && (Date.now() - showGoalStart < 5000) ? "block" : "none";

    previousStatus = status;
}
