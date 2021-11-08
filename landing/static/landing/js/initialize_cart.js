function initialize_cart(){
    console.log("Init!!!");
    var allCountersList = [].slice.call(document.querySelectorAll('input[name=cart-counter]'));
    console.log(allCountersList.length);

    for (let i = 0; i < allCountersList.length; i++){
        console.log(allCountersList[i].getAttribute("value"));
        console.log(allCountersList[i].getAttribute("id"));
    }
    var countersList = allCountersList.map((counter) => {
        var id = counter.getAttribute("id");
        id = id.slice(13);
        var cart_counter = $("#cart_counter_" + id);
        var decrement = $("#decrement_" + id);
        var increment = $("#increment_" + id);
        decrement.on("click", function(){
            if (cart_counter.val() > 1){
                var value = parseInt(cart_counter.val());
                console.log(value);
                cart_counter.val(value - 1);
                $("#cart-save").css("visibility", "visible");
            }
        });
        increment.on("click", function(){
            var value = parseInt(cart_counter.val());
            console.log(value);
            cart_counter.val(value + 1);
            $("#cart-save").css("visibility", "visible");
        });
        cart_counter.on("change", function(event){
            event.preventDefault();
            console.log("Changed!!!!!!!");
            console.log($("#cart_counter_" + id).val());
            $("#cart-save").css("visibility", "visible");
            console.log(counter.getAttribute("value"));
        });
        console.log("AJAX-Setup");
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
    var save_button = $("#cart-save");
    save_button.on("click", function(event){
        var countersList = [].slice.call(document.querySelectorAll('input[name=cart-counter]'));
        event.preventDefault();
        var dict = {};
        for (let i = 0; i < countersList.length; i++){
            var counter = countersList[i];
            var id = counter.getAttribute("id");
            id = id.slice(13);
            let cart_counter_jquery = $("#cart_counter_" + id);
            if (counter.getAttribute("value") !== cart_counter_jquery.val()){
                console.log("Indiscrepancy!");
                dict[id] = cart_counter_jquery.val();
            }
            console.log(dict);
        }
        $.ajax({
            url: '/update-order-from-side-cart/',
            type: 'POST',
            data: dict,
            success : function(json) {
                console.log(json);
                console.log("Successfully sent data");
                save_button.css("visibility", "hidden");
                for (let i = 0; i < json['items'].length; i++){
                    Object.entries(json['items'][i]).forEach(([key, value]) => {
                        $("#order_item_sum_" + key).text(value);
                    });
                }
                $("#order_price").text(json['cool_price'] + " руб.");
                // location.reload();
            },
            error : function(xhr, errmsg, err){
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

        /*$(function() {
            console.log("AJAX-Setup");
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

            /!*
            The functions below will create a header with csrftoken
            *!/

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
                    !(/^(\/\/|http:|https:).*!/.test(url));
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

        });*/
    });
}