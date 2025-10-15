# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This project template contains starter code for our class project. The `/service/models` folder contains `order.py` file and `orderitem.py` for our model and a `routes.py` file for our service. The `/tests` folder has test case starter code for testing the model and the service separately. We used the [sample-accounts](https://github.com/nyu-devops/sample-accounts.git) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── routes.py              - module with service routes
├── models
│   ├── __init__.py        - package initializer
│   ├── order.py           - module with order model
│   ├── orderitem.py       - module with subordinate order item model
│   └── persistent_base.py - Persistence base classes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_order.py          - test suite for order
├── test_orderitem.py      - test suite for subordinate order item
└── test_routes.py         - test suite for service routes

```

## Information about this repo

These are the RESTful routes for `orders` and `orderitems`

```
Endpoint             Methods  Rule
-------------------  -------  -----------------------------------------------------
index                GET      /

list_orders          GET      /orders
create_orders        POST     /orders
get_orders           GET      /orders/<order_id>
update_orders        PUT      /orders/<order_id>
delete_orders        DELETE   /orders/<order_id>

list_orderitems      GET      /orders/<int:order_id>/orderitems
create_orderitems    POST     /orders/<order_id>/orderitems
get_orderitems       GET      /orders/<order_id>/orderitems/<orderitem_id>
update_orderitems    PUT      /orders/<order_id>/orderitems/<orderitem_id>
delete_orderitems    DELETE   /orders/<order_id>/orderitems/<orderitem_id>
```

The test cases have 95% test coverage and can be run with `pytest`

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
