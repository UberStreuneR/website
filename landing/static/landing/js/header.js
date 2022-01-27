// function load_header_dropdown() {
//     $.ajax({
//         url: '/ajax-get-all-partners/',
//         type: 'GET',
//         success : function(json) {
//             for (let i = 0; i < json['partners'].length; i++){
//                 var key = Object.keys(json['partners'][i])[0];
//                 var value = Object.values(json['partners'][i])[0];
//                 var ul = $("#dropdown-ul");
//                 if (ul.length) {
//                     ul[0].innerHTML += "<li><a class=\"dropdown-item text-decoration-none\" href=\"" + value + "\">" + key + "</a></li>";
//                 }
//                 else {
//                     // $("#dropdown-div")[0].innerHTML += "<li><a class=\"dropdown-item text-decoration-none\" href=\"" + value + "\">" + key + "</a></li>";
//                 }
//             }
//         },
//         error : function(xhr, errmsg, err){
//             console.log(xhr.status + ": " + xhr.responseText);
//         }
//     });
// }

function load_header_dropdown() {
    $.ajax({
        url: '/ajax-get-all-partners/',
        type: 'GET',
        success : function(json) {
            for (let i = 0; i < json['partners'].length; i++){
                // console.log(json['partners'][i]);
                var key = Object.keys(json['partners'][i])[0];
                var value = Object.values(json['partners'][i])[0];
                var div = document.createElement("div");
                console.log(div);
                $("#dropdown-column-" + i%3).append(div);
                var flex = document.createElement("div");
                flex.classList.add("d-flex", "flex-column", "mb-3");
                console.log(flex);
                var categories = json['partners'][i]['categories'];
                for (let j = 0; j < categories.length; j++){
                    var category_key = Object.keys(categories[j])[0];
                    var category_value = Object.values(categories[j])[0];
                    // console.log(j, category_key, category_value);
                    flex.innerHTML += "<a class=\"text-decoration-none text-black px-0\" href=\"" + category_value + "\">" + category_key + "</a>";
                }
                div.innerHTML += "<h3 class='mb-1'>" + key + "</h3>";
                div.append(flex);
            }
        },
        error : function(xhr, errmsg, err){
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}


if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
    $("html").addClass("mobile");
    $(".screen").addClass("mobile");
}
