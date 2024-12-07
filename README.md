# Simple Subscription Web App with Stripe

This is a simple web application that implements Stripe subscription functionality using Flask and SQLite.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Stripe keys:
   - Sign up for a Stripe account if you haven't already
   - Get your API keys from the Stripe Dashboard
   - Update the `.env` file with your Stripe API keys
   - Update the price IDs in `templates/index.html` with your Stripe product price IDs

3. Initialize the database:
   - The database will be automatically created when you run the application for the first time

4. Run the application:
```bash
python app.py
```

## Features

- User subscription management
- Stripe integration for payment processing
- Basic and Premium subscription plans
- SQLite database for user data storage
- Success and cancellation handling

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
  - `index.html`: Homepage with subscription options
  - `success.html`: Successful subscription page
  - `cancel.html`: Cancelled subscription page
- `requirements.txt`: Project dependencies
- `.env`: Environment variables configuration

## Important Notes

- Make sure to replace `YOUR_PUBLISHABLE_KEY` in `index.html` with your actual Stripe publishable key
- Replace the price IDs (`YOUR_BASIC_PRICE_ID` and `YOUR_PREMIUM_PRICE_ID`) with your actual Stripe price IDs
- Never commit your `.env` file with real API keys to version control
