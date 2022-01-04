var script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);
var is_mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

function load_cart() {
    var tbody = $("#cart_tbody")[0];
    tbody.innerHTML = "";
    var tbody_elem = $("#cart_tbody");
    var cart = get_cart_items();
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
        } else {
            item_price = "цена по запросу"
        }
        var input_width;
        var price_string = "";
        if (is_mobile) {
            input_width = "2rem";
        } else {
            input_width = "40px";
            price_string = "<td>" + numberWithCommas(price) + "</td>";
        }
        tbody.innerHTML += "<tr>" +
            // tbody.append("<tr>" +
            "<th scope='row'>" + count + "</th>" +
            "<td><a style='text-decoration: none; color: black;' href='" + url + "'>" + name + "</a></td>" + price_string +
            // "<td>" + numberWithCommas(price) + "</td>" +
            "<td><div>" + "<a style=\"margin-right: 5px;\" id=\"cart_decrement_" + article + "\"><i class=\"fas fa-minus text-black\"></i></a>" +
            "<input value=\"" + value + "\" id=\"cart_counter_" + article + "\" name=\"cart-counter\" class=\"text-center side\" style='width: " + input_width + "'>" +
            "<a style=\"margin-left: 5px;\" id=\"cart_increment_" + article + "\"><i class=\"fas fa-plus text-black\"></i></a>" +
            "<div id=\"slug_" + article + "\" style=\"display: none;\">" + slug + "</div>" +

            "</div></td>" +
            "<td align='right'><span id=\"order_item_sum_" + article + "\">" + numberWithCommas(item_price) + "</span></td>" +
            "<td><a id=\"cart_remove_" + article + "\"><i class=\"fas fa-times text-danger\"></i></a></td></tr>"
        ;
        count += 1;
    }
    if (sum_price < 10000) {
        tbody.innerHTML +=  "<tr>\n" +
            "<th scope='row'>" + count + "</th>" +
        "                    <td colspan=\"3\">Доставка в пределах МКАД для заказа до 10000 руб.</td>\n" +
        "                    <td align='right' colspan=\"1\">800</td>\n" +
            "<td style='visibility: hidden;'><a style='pointer-events: none;'><i class=\"fas fa-times text-danger\"></i></a></td></tr>" +
        "                </tr>";
    }
    var sum_with_delivery = parseInt(cart_sum());
    console.log(sum_with_delivery);
    console.log(cart_sum());
    if (cart_sum() < 10000) {
        sum_with_delivery += 800;
    }
    if (is_mobile) {
        tbody.innerHTML += "<tr>\n" +
            "                    <td colspan=\"2\"><b><h3>Сумма заказа</h3></b></td>\n" +
            "                    <td colspan=\"2\"><b><h3 id=\"order_price\">" + numberWithCommas(sum_with_delivery) + " руб.</h3></b></td>\n" +
            "                </tr>";
    }
    else {
        tbody.innerHTML += "<tr>\n" +
        "                    <td colspan=\"3\"><b><h3>Сумма заказа</h3></b></td>\n" +
        "                    <td colspan=\"2\"><b><h3 id=\"order_price\">" + numberWithCommas(sum_with_delivery) + " руб.</h3></b></td>\n" +
        "                </tr>";
    }

   /* var order_price = $("#order-price");
    order_price.text("Итого: " + numberWithCommas(sum_price) + " руб.");*/
    var allCountersList = [].slice.call(document.querySelectorAll('input[name=cart-counter]'));
    var countersList = allCountersList.map((counter) => {
        var id = counter.getAttribute("id");
        id = id.slice(13);
        console.log(id);
        var j_counter = $("#cart_counter_" + id);
        var decrementButton = document.querySelector("a[id=cart_decrement_" + id + "]");
        var incrementButton = document.querySelector("a[id=cart_increment_" + id + "]");
        var crossButton = document.querySelector("a[id=cart_remove_" + id + "]");
        var item_sum = $("#order_item_sum_" + id);
        decrementButton.addEventListener("click", function() {
            console.log("decrement", id);
            if (counter.value > 1){
                decrement_cart_item(id);
                j_counter.val(get_cart_item_value(id)['value']);
                update_sum();
                item_sum.text(numberWithCommas(parseInt(j_counter.val()) * get_cart_item_price(id)));
            }
        });
        incrementButton.addEventListener("click", function() {
            console.log("increment", id);
            increment_cart_item(id);
            j_counter.val(get_cart_item_value(id)['value']);
            update_sum();
            item_sum.text(numberWithCommas(parseInt(j_counter.val()) * get_cart_item_price(id)));
        });
        crossButton.addEventListener("click", function() {
            delete_cart_item(id);
            load_cart();
        });
        j_counter.on("change", () => {
            if (parseInt(j_counter.val())) {
                update_cart_item_value(id, j_counter.val());
                update_sum();
                item_sum.text(numberWithCommas(parseInt(j_counter.val()) * get_cart_item_price(id)));
            }
        });
        function update_sum() {
            $("#order_price").text(cart_sum() + " руб.");
        }
    });
}