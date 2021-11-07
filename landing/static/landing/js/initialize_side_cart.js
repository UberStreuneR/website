function initialize(){
    console.log("Init!!!");
    var allCountersList = [].slice.call(document.querySelectorAll('input[name=side-cart-counter]'));
    console.log(allCountersList.length);
    if (allCountersList.length === 0){
        $("#side-cart-count").text("0").removeClass("bg-danger").addClass("bg-dark");
    }
    else {
        console.log("NOT ZERO");
    }
    for (let i = 0; i < allCountersList.length; i++){
        console.log(allCountersList[i].getAttribute("value"));
        console.log(allCountersList[i].getAttribute("id"));
    }
    var countersList = allCountersList.map((counter) => {
        var id = counter.getAttribute("id");
        id = id.slice(13);
        var side_counter = $("#side_counter_" + id);
        var side_decrement = $("#side_decrement_" + id);
        var side_increment = $("#side_increment_" + id);
        var side_remove_item = $("#side_cart_remove_" + id);
        side_decrement.on("click", function(){
            if (side_counter.val() > 1){
                var value = parseInt(side_counter.val());
                console.log(value);
                side_counter.val(value - 1);
                $("#side-cart-save").css("visibility", "visible");
            }
        });
        side_increment.on("click", function(){
            var value = parseInt(side_counter.val());
            console.log(value);
            side_counter.val(value + 1);
            $("#side-cart-save").css("visibility", "visible");
        });
        side_counter.on("change", function(event){
            event.preventDefault();
            console.log("Changed!!!!!!!");
            console.log($("#side_counter_" + id).val());
            $("#side-cart-save").css("visibility", "visible");
            console.log(counter.getAttribute("value"));
        });
        side_remove_item.on("click", function(event){
            event.preventDefault();
            console.log("Delete!!!!!!!");
            $.ajax({
            url: '/ajax-remove-from-cart/',
            type: 'POST',
            data: {'article': id},
            success : function(json) {
                console.log(json);
                console.log("Success");
                $("#order-price").text("Итого: " + json['cool_price'] + " руб.");
                /*if (json['empty'] === 'True'){
                    console.log("EMPTY");
                    $("#side-cart-count").text(0).removeClass("bg-danger").addClass("bg-dark");
                }*/
                get_order_items();
            },
            error : function(xhr, errmsg, err){
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
        });
    });
    var save_button = $("#side-cart-save");
    save_button.on("click", function(event){
        var sideCountersList = [].slice.call(document.querySelectorAll('input[name=side-cart-counter]'));
        event.preventDefault();
        var dict = {};
        for (let i = 0; i < sideCountersList.length; i++){
            var counter = sideCountersList[i];
            var id = counter.getAttribute("id");
            id = id.slice(13);
            let side_counter_jquery = $("#side_counter_" + id);
            if (counter.getAttribute("value") !== side_counter_jquery.val()){
                dict[id] = side_counter_jquery.val();
            }
        }
        $.ajax({
            url: '/update-order-from-side-cart/',
            type: 'POST',
            data: dict,
            success : function(json) {
                console.log(json);
                console.log("Success");
                save_button.css("visibility", "hidden");
                $("#order-price").text("Итого: " + json['cool_price'] + " руб.");
                get_order_items();
            },
            error : function(xhr, errmsg, err){
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

        $(function() {
            // This function gets cookie with a given name
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            var csrftoken = getCookie('csrftoken');

            /*
            The functions below will create a header with csrftoken
            */

            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            function sameOrigin(url) {
                // test that a given url is a same-origin URL
                // url could be relative or scheme relative or absolute
                var host = document.location.host; // host + port
                var protocol = document.location.protocol;
                var sr_origin = '//' + host;
                var origin = protocol + sr_origin;
                // Allow absolute or scheme relative URLs to same origin
                return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                    // or any other URL that isn't scheme relative or absolute i.e relative.
                    !(/^(\/\/|http:|https:).*/.test(url));
            }

            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                        // Send the token to same-origin, relative URLs only.
                        // Send the token only if the method warrants CSRF protection
                        // Using the CSRFToken value acquired earlier
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

        });
    });
}