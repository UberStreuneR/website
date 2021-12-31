var script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function numberWithCommas(x) {
    if (x === "цена по запросу") {
        return x;
    }
    if (x === -2) {
        return "цена по запросу";
    }
    if (x === -1) {
        return "нет в наличии";
    }
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
function update_cart_item(id, values) {
    var dict_string = getCookie("cart");
    var dict = JSON.parse(dict_string);
    if (dict[id] === undefined) {
        dict[id] = values;
    }
    else {
        dict[id]['value'] = parseInt(dict[id]['value']) + parseInt(values['value']);
    }
    document.cookie = 'cart = ' + JSON.stringify(dict) + ';domain=;path=/';
}
function update_cart_item_value(id, value) {
    var dict_string = getCookie("cart");
    var dict = JSON.parse(dict_string);
    dict[id]['value'] = value;
    document.cookie = 'cart = ' + JSON.stringify(dict) + ';domain=;path=/';
}
function increment_cart_item(id) {
    var dict_string = getCookie("cart");
    var dict = JSON.parse(dict_string);
    dict[id]['value'] = parseInt(dict[id]['value']) + 1;
    document.cookie = 'cart = ' + JSON.stringify(dict) + ';domain=;path=/';
}
function decrement_cart_item(id) {
    var dict_string = getCookie("cart");
    var dict = JSON.parse(dict_string);
    if (parseInt(dict[id]['value']) > 1) {
        dict[id]['value'] = parseInt(dict[id]['value']) - 1;
    }
    document.cookie = 'cart = ' + JSON.stringify(dict) + ';domain=;path=/';
}
function get_cart_item_value(id) {
    var dict_string = getCookie("cart");
    var dict = JSON.parse(dict_string);
    return dict[id];
}
function get_cart_items() {
    var dict_string = getCookie("cart");
    return JSON.parse(dict_string);
}
function delete_cart_item(id) {
    var dict = get_cart_items();
    delete dict[id];
    document.cookie = 'cart = ' + JSON.stringify(dict) + ';domain=;path=/';
}
function clear_cart() {
    document.cookie = "cart = {}" + ';domain=;path=/';
}
function load_side_cart() {
    var tbody = $("#table-body")[0];
    tbody.innerHTML = "";
    var cart = get_cart_items();
    var counter_span = $("#side-cart-count");
    if (Object.entries(cart).length > 0) {
        counter_span.removeClass("bg-dark").addClass("bg-danger");
        counter_span.text(Object.entries(cart).length);
    }
    else {
        counter_span.removeClass("bg-danger").addClass("bg-dark");
        counter_span.text(0);
    }
    var count = 1;
    var sum_price = 0;
    for (const [id, values] of Object.entries(cart)) {
        var article = id;
        var value = values['value'];
        var name = values['name'];
        var price = values['price'];
        var url = values['url'];
        var slug = values['slug'];
        if (parseInt(price) > 0) {
            var item_price = price * value;
            sum_price += item_price;
        }
        else {
            item_price = "цена по запросу"
        }

        tbody.innerHTML += "<tr>" +
            "<th scope='row'>" + count + "</th>" +
            "<td><a style='text-decoration: none; color: black;' href='" + url +  "'>" + name + "</a></td>" +
                "<td>" + numberWithCommas(price) + "</td>" +
                "<td><div>" + "<a style=\"margin-right: 5px;\" id=\"side_decrement_" + article + "\"><i class=\"fas fa-minus text-black\"></i></a>" +
                "<input value=\"" + value + "\" id=\"side_counter_" + article + "\" name=\"side-cart-counter\" class=\"text-center side\" style=\"width: 40px;\">" +
                "<a style=\"margin-left: 5px; margin-right: 10px;\" id=\"side_increment_" + article + "\"><i class=\"fas fa-plus text-black\"></i></a>" +
                "<div id=\"slug_" + article + "\" style=\"display: none;\">" + slug + "</div>" +

            "</div></td>" +
                "<td align='right'><span id=\"order_item_sum_" + article + "\">" + numberWithCommas(item_price) + "</span></td>" +
                "<td><a id=\"side_cart_remove_" + article + "\"><i class=\"fas fa-times text-danger\"></i></a></td></tr>"
            ;
        count += 1;

    }
    var order_price = $("#order-price");
    order_price.text("Итого: " + numberWithCommas(sum_price) + " руб.")
    var allCountersList = [].slice.call(document.querySelectorAll('input[name=side-cart-counter]'));
    var countersList = allCountersList.map((counter) => {
        var id = counter.getAttribute("id");
        id = id.slice(13);
        var decrementButton = document.querySelector("a[id=side_decrement_" + id + "]");
        var incrementButton = document.querySelector("a[id=side_increment_" + id + "]");
        var removeButton = document.querySelector("a[id=side_cart_remove_" + id + "]");
        var j_counter = $("#side_counter_" + id);
        var listview_div = $("#listview-item-div-" + id);
        var tileview_div = $("#tileview_item_div_" + id);

        decrementButton.addEventListener("click", function() {
            if (counter.value > 1){
                counter.value = parseInt(counter.value) - 1;
            }
            update_cart_item_value(id, counter.value);
            load_side_cart();
        });
        incrementButton.addEventListener("click", function() {
            counter.value = parseInt(counter.value) + 1;
            update_cart_item_value(id, counter.value);
            load_side_cart();
        });
        removeButton.addEventListener("click", function() {
            delete_cart_item(id);
            load_side_cart();
            if (listview_div.length) {
                $("#listview-counter-" + id).val(1);
                listview_div.css("visibility", "hidden");
            }
            if (tileview_div.length) {
                $("#counter_" + id).val(1);
                tileview_div.removeClass("d-inline").addClass("d-none");
            }
        });
        j_counter.on("change", () => {
            if (listview_div.length) {
                $("#listview-counter-" + id).val(j_counter.val());
            }
            if (tileview_div.length) {
                $("#counter_" + id).val(j_counter.val());
            }
            update_cart_item_value(id, j_counter.val());
            load_side_cart();
        });
    });
}