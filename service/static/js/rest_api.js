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
        $("#order_status").val("");

        $("#order_total").val("");
        $("#created_at").val("");
        $("#updated_at").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }


}  );
