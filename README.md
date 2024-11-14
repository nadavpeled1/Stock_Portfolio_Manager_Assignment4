# Stock Portfolio Management REST Application

This project is a REST application for managing a stock portfolio.
It allows users to manage stocks in a given portfolio, retrieve stock prices, and compute the value of the portfolio based on the latest recorded prices.
The application uses a 3rd party API to retrieve stock prices and runs in a Docker container.

## Architecture

The application follows a controller-service architecture, where the controller module handles incoming HTTP requests and invokes the appropriate methods in the service module.
The service module contains the business logic for managing stocks, retrieving stock prices, and computing the portfolio value. It also interacts with a 3rd party API to retrieve stock prices.

## Features

- Manage stocks in a portfolio
- Retrieve stock prices on a given day
- Compute the value of the portfolio based on the latest recorded prices
- Use a 3rd party API to retrieve stock prices
- Run the application in a Docker container
