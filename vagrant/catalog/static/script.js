document.addEventListener("DOMContentLoaded", function(event){

    document.querySelectorAll(".category-element").forEach(
        function(button){
            button.addEventListener("click",
              categoryElementOnClick.bind(null,
                button,
                ".category-element.active",
                "/course/"+button.dataset.name),
              false);
        }
    );

    document.querySelectorAll(".course-item-element").forEach(
        function(button){
            button.addEventListener("click",
              categoryElementOnClick.bind(null,
                button,
                ".course-item-element.active",
                "/course/"+button.dataset.courseName+"/"+button.dataset.name),
              false);
        }
    );
});

function signInCallback(authResult){
    if(authResult['code']){
        document.getElementById("signInButton").style.display = "none";
        var state = document.getElementById("pydata").dataset.state;
        console.log('state is -----'+state);
        var url = '/gconnect?state='+state
        console.log(authResult['code']);

        var httpRequest = new XMLHttpRequest();
        httpRequest.onreadystatechange = function() {
            if (httpRequest.readyState == XMLHttpRequest.DONE) {
                window.location.reload();
            }
        }
        httpRequest.open('POST', url, true);
        httpRequest.setRequestHeader('Content-Type','application/octet-stream; charset=utf-8');
        httpRequest.send(authResult['code']);
        // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page

    }
}

function categoryElementOnClick(button,selector,href){
    active = document.querySelector(selector);
    if(active !== null){
        active.classList.remove("active");
    }

    button.classList.add("active");
    location.href = href;
}