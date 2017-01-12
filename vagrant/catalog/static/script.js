document.addEventListener("DOMContentLoaded", function(event){

    buttons = document.querySelectorAll(".category-element");
    buttons.forEach(function(button){
        button.addEventListener("click",categoryElementOnClick, false);
    });
});

function categoryElementOnClick(){
    active = document.querySelector(".category-element.active");
    if(active !== null){
        active.classList.remove("active");
    }

    this.classList.add("active");
    console.log(location.href);
    console.log(this.dataset.name);
    location.href = this.dataset.name;
}