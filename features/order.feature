Feature: The order service back-end
    As a Order Service Owner
    I need a RESTful order service
    So that I can keep track of all customer orders

Background:
    Given the following orders
        | customer_id | order_status   |
        | 1001        | 0              |
        | 1001        | 1              |
        | 1002        | 2              |
        | 1001        | 3              |
        | 1002        | 4              |
        | 1002        | 5              |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer ID" to "1003"
    And I set the "Order Status" to "0"
    And I press the "Create" button
    Then I should see the message "Success"