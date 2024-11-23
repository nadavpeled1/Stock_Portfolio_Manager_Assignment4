from controller import StockController


def main():
    """
    Entry point for the Stock Portfolio Manager application.
    Initializes the StockController and runs the Flask app.
    """
    try:
        # Initialize the StockController
        controller = StockController()

        # Run the Flask app
        controller.app.run(host='0.0.0.0', port=5001)

    except Exception as e:
        print(f"Error starting the Stock Portfolio Manager: {str(e)}")


if __name__ == '__main__':
    main()