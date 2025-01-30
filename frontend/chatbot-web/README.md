# Chatbot Web Interface

This project provides a simple web interface for an existing chatbot functionality that retrieves street information and famous person information based on the street name.

## Project Structure

```
chatbot-web
├── src
│   ├── chatbot.py          # Contains the chatbot functionality
│   ├── app.py              # Entry point for the web application
│   ├── templates
│   │   └── index.html      # HTML template for the web interface
│   └── static
│       └── styles.css      # CSS styles for the web interface
├── requirements.txt        # Lists project dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot-web
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the web application:
   ```
   python src/app.py
   ```

4. Open your web browser and go to `http://127.0.0.1:5000` to access the chatbot interface.

## Usage Guidelines

- Enter a street name in the provided form and submit to retrieve information about the street and any associated famous person.
- The chatbot will display the street information and any relevant details about the famous person linked to the street name.

## License

This project is licensed under the MIT License.