$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
        $("#total_amount").val(res.total_amount);
        $("#created_at").val(res.created_at);
        $("#updated_at").val(res.updated_at);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#customer_id").val("");
        $("#order_status").val("CREATED");
        $("#total_amount").val("");
        $("#created_at").val("");
        $("#updated_at").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let order_status = $("#order_status").val();
        let now = new Date().toISOString();

        let data = {
            "customer_id": customer_id,
            "status": order_status,
            "created_at": now,
            "updated_at": now
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {
        let order_id = $("#order_id").val(); //this remains #order_id becasue this is the currently loaded order
        let customer_id = $("#customer_id").val();
        let order_status = $("#order_status").val();
        let created_at = $("#created_at").val();
        
        // Update the updated_at timestamp
        let updated_at = new Date().toISOString();

        let data = {
            "customer_id": customer_id,
            "status": order_status,
            "created_at": created_at,
            "updated_at": updated_at
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
            list_orders();

        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {
    let order_id = $("#order_id_search").val().trim();
    let customer_id = $("#customer_id").val();

    $("#flash_message").empty();

    // 如果 order_id 为空，则通过 customer_id 搜索
    if (!order_id && customer_id) {
        let ajax = $.ajax({
            type: "GET",
            url: `/orders?customer_id=${customer_id}`,
            contentType: "application/json"
        });

        ajax.done(function(res){
            if (res && res.length > 0) {
                update_form_data(res[0]);
                flash_message("Success");
            } else {
                flash_message("No order found");
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    } else {
        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json"
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    }
    });
    

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {
        let order_id = $("#order_id_search").val().trim();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            flash_message("Success");
            list_orders();

        });

        ajax.fail(function(res){
            flash_message("Server error!");
        });
    });

    // ****************************************
    // Clear Form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });



// ****************************************
// List ORDERS
// ****************************************

  function render_orders_table(orders) {
    const $tbody = $("#orders_table_body");
    $tbody.empty();

    if (!orders || orders.length === 0) {
      $tbody.append(`<tr><td colspan="6"><em>No orders found</em></td></tr>`);
      return;
  }

  orders.forEach(order => {
    const id = order.id ?? "";
    const customer_id = order.customer_id ?? "";
    const status = order.status ?? "";
    const total = order.total_amount ?? "";
    const created = order.created_at ?? "";

    $tbody.append(`
      <tr>
        <td>${id}</td>
        <td>${customer_id}</td>
        <td>${status}</td>
        <td>${total}</td>
        <td>${created}</td>
        <td></td>
      </tr>
    `);
  });
}

function list_orders(customer_id = "") {
  const url = customer_id
    ? `/orders?customer_id=${encodeURIComponent(customer_id)}`
    : "/orders";

  $.ajax({ type: "GET", url, contentType: "application/json" })
    .done(function (res) {
      const orders = Array.isArray(res) ? res : (res.orders || []);
      render_orders_table(orders);
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Could not load orders");
    });
}

$("#list_all_orders-btn").click(function () {
  list_orders("");
  flash_message(`Listed all orders`);


});

$("#list_by_customer-btn").click(function () {
  list_orders($("#customer_id").val().trim());
  flash_message(`Listed customer's orders`);
});



// ****************************************
// ORDER ITEMS
// ****************************************


//RETRIEVE

function update_item_form(res) {
  const item_id = res.id ?? res.item_id ?? "";
  $("#item_id").val(item_id);
  $("#item_id_search").val(item_id); // optional sync
  $("#item_product_id").val(res.product_id ?? "");
  $("#item_quantity").val(res.quantity ?? "");
  $("#item_unit_price").val(res.price ?? res.unit_price ?? "");
}
$("#retrieve_item-btn").click(function () {
  const order_id = $("#order_id").val().trim();
  const item_id = $("#item_id_search").val().trim();

  if (!order_id) return flash_message("Retrieve an order first (Order ID is required).");
  if (!item_id) return flash_message("Item ID is required.");

  $.ajax({
    type: "GET",
    url: `/orders/${encodeURIComponent(order_id)}/orderitems/${encodeURIComponent(item_id)}`,
    contentType: "application/json",
  })
  .done(function (res) {
    update_item_form(res);
    flash_message("Success");
  })
  .fail(function (res) {
    flash_message(res.responseJSON?.message || "Item not found");
  });
});



///LIST

function render_items(items) {
  $("#items_table_body").empty();

  items.forEach(function (it) {
    const id = it.id ?? it.item_id ?? "";
    const product_id = it.product_id ?? "";
    const qty = it.quantity ?? "";
    const price = it.price ?? it.unit_price ?? "";
    const line = it.line_amount ?? it.line_total ?? "";

    $("#items_table_body").append(`
      <tr>
        <td>${id}</td>
        <td>${product_id}</td>
        <td>${qty}</td>
        <td>${price}</td>
        <td>${line}</td>
      </tr>
    `);
  });
}

function list_items_for_current_order() {
  const order_id = $("#order_id").val();
  if (!order_id) return;

  $.ajax({
    type: "GET",
    url: `/orders/${order_id}/orderitems`,   // <-- change to /items if that's your API
    contentType: "application/json",
  })
  .done(function (res) {
    render_items(res);
  })
  .fail(function () {
    // optional: flash_message("Failed to list items");
  });
}

$("#list_all_order_items-btn").click(function () {
  list_items_for_current_order("");
  flash_message(`Listed all order's items`);
});


// ****************************************
// CREATE AN ORDER ITEM
// ****************************************


    $("#create_item-btn").click(function () {
    const order_id = parseInt($("#order_id").val(), 10);   // current order (readonly)
    const product_id = $("#item_product_id").val().trim();
    const price = parseFloat($("#item_unit_price").val());
    const quantity = parseInt($("#item_quantity").val(), 10);

    //make sure there are order id for which to add to 
    if (!order_id) return flash_message("Create or Retrieve an order first (Order ID is required).");
    if (!product_id) return flash_message("Product ID is required.");
    if (!Number.isFinite(price) || price < 0) return flash_message("Unit Price must be a valid number >= 0.");
    if (!Number.isInteger(quantity) || quantity <= 0) return flash_message("Quantity must be a positive integer.");

    
    const data = { order_id, product_id, price, quantity };

    //send post to orderitems with the desirialize
    $.ajax({
        type: "POST",
        url: `/orders/${order_id}/orderitems`,
        contentType: "application/json",
        data: JSON.stringify(data)
    })
    .done(function () {
    flash_message("Item created");
    list_items_for_current_order();
    })
    .fail(function (res) {
        flash_message(res.responseJSON?.message || "Failed to create item");
    });
});

function clear_item_form_data() {
  $("#item_id_search").val("");
  $("#item_id").val("");
  $("#item_product_id").val("");
  $("#item_quantity").val("");
  $("#item_unit_price").val("");
}

// Clear Item Form button
$("#clear_item-btn").click(function () {
  clear_item_form_data();
  flash_message("Item form cleared");
});



list_orders();

}  );
