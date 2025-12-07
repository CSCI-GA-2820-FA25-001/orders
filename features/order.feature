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
    And I set the "customer_id" to "1999"
    And I select "CREATED" in the "order_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "order_id" field
    And I press the "Clear" button
    Then the "order_id" field should be empty
    And the "customer_id" field should be empty
    When I paste the "order_id_search" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1999" in the "customer_id" field
    And I should see "CREATED" in the "order_status" dropdown

Scenario: Update an Order
    When I visit the "Home Page"
    And I set the "customer_id" to "1002"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I copy the "order_id" field
    And I change "customer_id" to "1002-UPDATED"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    When I paste the "order_id_search" field
    And I press the "Retrieve" button
    Then I should see "1002-UPDATED" in the "customer_id" field

Scenario: Delete an Order
    When I visit the "Home Page"
    And I set the "customer_id" to "1002"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I copy the "order_id" field
    When I press the "Clear" button
    And I paste the "order_id_search" field
    And I press the "Delete" button
    Then I should see the message "Success"

Scenario: Create an Order Item successfully
    When I visit the "Home Page"
    And I set the "customer_id" to "1999"
    And I select "CREATED" in the "order_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "order_id" field

    When I set the "item_product_id" to "SKU123"
    And I set the "item_quantity" to "2"
    And I set the "item_unit_price" to "19.99"
    And I press the "Create Item" button
    Then I should see the message "Item created"