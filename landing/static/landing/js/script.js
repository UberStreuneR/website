function get_order_items(){
    $.ajax({
        url: '/ajax-get-order-items/',
        type: 'GET',
        success : function(json) {
            console.log(json);
            /*if (json['empty'] == 'True'){
                console.log("Empty");
                $("#side-cart-count").text("0").removeClass("bg-danger").addClass("bg-dark");
            }
            else {
                console.log("Not empty");
            }*/
            if ($("#table-body").length){
                $("#table-body")[0].innerHTML = "";
            }
            for (let i = 0; i < json['order']['items'].length; i++){
                var order_item = json['order']['items'][i];
                var item = order_item['item'];
                console.log(order_item);
                $("#side-cart-count").text(json['order']['items'].length).removeClass("bg-dark").addClass("bg-danger");
                var count = parseInt(i) + 1;
                $("#table-body")[0].innerHTML += "<tr>" +
                    "<th scope='row'>" + count + "</th>" +
                    "<td><a style='text-decoration: none; color: black;' href='" + item['url'] +  "'>" + item.name + "</a></td>" +
                        "<td>" + item['cool_price'] + "</td>" +
                        "<td><div>" + "<a style=\"margin-right: 5px;\" id=\"side_decrement_" + item['article'] + "\"><i class=\"fas fa-minus text-black\"></i></a>" +
                        "<input value=\"" + order_item['quantity'] + "\" id=\"side_counter_" + item['article'] + "\" name=\"side-cart-counter\" class=\"text-center side\" style=\"width: 40px;\">" +
                        "<a style=\"margin-left: 5px; margin-right: 10px;\" id=\"side_increment_" + item['article'] + "\"><i class=\"fas fa-plus text-black\"></i></a>" +
                        "<div id=\"slug_" + item['article'] + "\" style=\"display: none;\">" + item['slug'] + "</div>" +

                    "</div></td>" +
                        "<td align='right'><span id=\"order_item_sum_" + item['article'] + "\">" + order_item['cool_price'] + "</span></td>" +
                        "<td><a id=\"side_cart_remove_" + item['article'] + "\"><i class=\"fas fa-times text-danger\"></i></a></td></tr>"
                ;
            }
            $("#order-price").text("Итого: " + json['order']['cool_price'] + " руб.");
            initialize();
        },
        error : function(xhr, errmsg, err){
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
