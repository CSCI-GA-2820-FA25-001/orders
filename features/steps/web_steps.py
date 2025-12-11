######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import re
import logging
import time
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = ""


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('I should see "{text}" in the "{table_id}" table')
def step_impl(context, text, table_id):
    table = context.driver.find_element(By.ID, table_id)
    assert (
        text in table.text
    ), f'Did not find "{text}" in table #{table_id}. Table text was:\n{table.text}'


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    # save_screenshot(context, message)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I press the "{button_name}" button for the first order')
def step_impl(context, button_name):
    """Press a button in the first row of the orders table"""
    button_mapping = {"Cancel": "cancel-order-btn"}

    button_class = button_mapping.get(
        button_name, button_name.lower().replace(" ", "-") + "-btn"
    )

    wait = WebDriverWait(context.driver, 2)
    max_retries = 5
    for attempt in range(max_retries):
        try:
            element = wait.until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, button_class)
                )
            )
            context.driver.execute_script("arguments[0].click();", element)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(0.5)

    if button_name == "Cancel":
        alert = WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.alert_is_present()
        )
        alert.accept()


@then('I should see "{button_text}" button for orders with "{status}" status')
def step_impl(context, button_text, status):
    """Verify that cancel button appears for orders with specific status"""
    wait = WebDriverWait(context.driver, context.wait_seconds)

    wait.until(
        expected_conditions.presence_of_element_located((By.ID, "orders_table_body"))
    )

    rows = context.driver.find_elements(By.CSS_SELECTOR, "#orders_table_body tr")
    found_button = False

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 6 and status in cells[2].text:
            actions_cell = cells[5]
            buttons = actions_cell.find_elements(By.CLASS_NAME, "cancel-order-btn")
            if len(buttons) > 0:
                found_button = True
                break

    assert found_button, f"Did not find {button_text} button for {status} status"


@then('I should not see "{button_text}" button for orders with "{status}" status')
def step_impl(context, button_text, status):
    """Verify that cancel button does not appear for orders with specific status"""
    wait = WebDriverWait(context.driver, context.wait_seconds)

    wait.until(
        expected_conditions.presence_of_element_located((By.ID, "orders_table_body"))
    )

    rows = context.driver.find_elements(By.CSS_SELECTOR, "#orders_table_body tr")

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 6 and status in cells[2].text:
            actions_cell = cells[5]
            buttons = actions_cell.find_elements(By.CLASS_NAME, "cancel-order-btn")
            assert (
                len(buttons) == 0
            ), f"Found unexpected {button_text} button for {status} status"
