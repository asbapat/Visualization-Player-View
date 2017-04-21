function checkTab(evt, tabName) {
    var i, tabcontent, tabStyles;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tabStyle" and remove the class "active"
    tabStyles = document.getElementsByClassName("tabStyle");
    for (i = 0; i < tabStyles.length; i++) {
        tabStyles[i].className = tabStyles[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    if(tabName === 'gameweek') {
        makeGameweekPlot();
    }
    else if(tabName === 'season') {
        collapsibleTree();
    }
}

var margin = {top: 20, right: 20, bottom: 30, left: 60},
    width = 960 - margin.left - margin.right,
    height = 430 - margin.top - margin.bottom;
