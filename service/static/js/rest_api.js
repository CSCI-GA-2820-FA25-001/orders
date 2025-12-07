$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
        $("#order_total").val(res.total_amount);
        $("#created_at").val(res.created_at);
        $("#updated_at").val(res.updated_at);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#customer_id").val("");
        $("#order_status").val("CREATED");
        $("#order_total").val("");
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
        let order_id = $("#order_id").val();
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
    let order_id = $("#order_id").val();
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
        let order_id = $("#order_id").val();

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
        list_orders(); 
    });

    // ****************************************
    // LIST ALL ORDERS
    // ****************************************


    // Render Orders List table
    function render_orders_table(orders) {
    const $tbody = $("#orders_table_body");
    $tbody.empty();

    if (!orders || orders.length === 0) {
        $tbody.append(`<tr><td colspan="5"><em>No orders found</em></td></tr>`);
        return;
    }

    orders.forEach(order => {
        const id = order.id ?? "";
        const customer_id = order.customer_id ?? "";
        const status = order.status ?? "";
        const total = order.total_amount ?? "";
        const created = order.created_at ?? "";

        $tbody.append(`
        <tr data-order-id="${id}">
            <td>${id}</td>
            <td>${customer_id}</td>
            <td>${status}</td>
            <td>${total}</td>
            <td>${created}</td>
        </tr>
        `);
    });
    }

    // Call API to list orders (optionally filtered by customer_id)
    function list_orders(customer_id = "") {
    const url = customer_id
        ? `/orders?customer_id=${encodeURIComponent(customer_id)}`
        : "/orders";

    $.ajax({
        type: "GET",
        url: url,
        contentType: "application/json",
    })
        .done(function (res) {
        const orders = Array.isArray(res) ? res : (res.orders || []);
        render_orders_table(orders);
        flash_message(`Loaded ${orders.length} order(s)`);
        })
        .fail(function (res) {
        flash_message(res.responseJSON?.message || "Could not load orders");
        });
    }
   $("#list-btn").click(function () { 
        
        list_orders(''); 
    });

    // ****************************************
    // LIST CUSTOMER ORDERS
    // ****************************************

    $("#list-by-customer-btn").click(function () { 
        //List orders filtered by customer_id (uses your existing query logic)
        const customer_id = $("#customer_id").val().trim(); 
        list_orders(customer_id); 
    });



   
list_orders(''); 
}  );
