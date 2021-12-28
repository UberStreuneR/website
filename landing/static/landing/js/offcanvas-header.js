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