let b = $("#fixed-offcanvas-btn");
b.on("click", () => {
    b.toggleClass("button-activated");
    if (b.hasClass("button-activated")) {
        b.html("<i class=\"fas fa-arrow-up\"></i>")
    }
    else {
        b.html("<i class=\"fas fa-bars\"></i>")
    }
});
$(document).on("click", e => {
    if (!e.target.matches("#fixed-offcanvas-btn") && !e.target.matches(".fas.fa-bars") && b.hasClass("button-activated")) { // element is not a button
        b.toggleClass("button-activated");                                                                                    // not an icon inside button
        if (b.hasClass("button-activated")) {                                                                               // button is activated
            b.html("<i class=\"fas fa-arrow-up\"></i>")
        }
        else {
            b.html("<i class=\"fas fa-bars\"></i>")
        }
    }
});
var header_height = $(".screen.mobile").height();
$(window).on("scroll", () => {
    if ($(window).scrollTop() > header_height) {
        b.addClass("btn-visible");
    }
    else {
        b.removeClass("btn-visible");
    }
});
$.ajax({
    url: '/ajax-get-all-partners/',
    type: 'GET',
    success : function(json) {
        for (let i = 0; i < json['partners'].length; i++){
            var key = Object.keys(json['partners'][i])[0];
            var value = Object.values(json['partners'][i])[0];
            $("#dropdown-ul-offcanvas")[0].innerHTML += "<li><a class=\"dropdown-item text-decoration-none\" href=\"" + value + "\">" + key + "</a></li>";
        }
    },
    error : function(xhr, errmsg, err){
        console.log(xhr.status + ": " + xhr.responseText);
    }
});

if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
    $("html").addClass("mobile");
    $(".screen").addClass("mobile");
}