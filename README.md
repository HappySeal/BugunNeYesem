# Food Recommendation Bot

A Telegram bot that analyzes your food ordering history from TGO Yemek and provides personalized recommendations.

## Features

- Parse TGO Yemek order history from JSON to CSV
- Automatically fetch fresh order data from TGO Yemek on demand
- View your recent order history
- Get personalized food recommendations based on your ordering patterns
- Get advanced AI-powered recommendations using Claude AI
- Find your top restaurants
- Simple and intuitive Telegram interface

## Files

- `parse_orders.py` - Parses order data from JSON to CSV format
- `food_recommendation_simple.py` - Analyzes order history and generates recommendations
- `food_recommendation.py` - Uses Claude AI for advanced recommendations
- `login_flow.py` - Handles logging in to TGO Yemek and fetching order data
- `food_recommendation_bot.py` - Telegram bot that integrates all functionality
- `claude_prompt_template.txt` - Template for AI recommendation prompts (customizable)

## Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install pyTelegramBotAPI python-dotenv requests
   ```
3. Create a Telegram bot by messaging [@BotFather](https://t.me/botfather) on Telegram
4. Rename `env_template.txt` to `.env` and add your credentials:
   ```
   # Telegram Bot token
   TELEGRAM_API_KEY=your_telegram_bot_token_here
   
   # TGO Yemek credentials
   TGO_USERNAME=your_tgo_email_here
   TGO_PASSWORD=your_tgo_password_here
   
   # (Optional) Claude AI API key
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
5. The bot is now ready to use. Your credentials are safely stored as environment variables.

## Usage

1. Run the Telegram bot:
   ```
   python food_recommendation_bot.py
   ```
2. Open the bot in Telegram and click "Start"
3. Use the menu buttons to:
   - Update order data (always fetches fresh data from TGO Yemek)
   - View your recent orders
   - Get personalized food recommendations
   - Get advanced AI recommendations from Claude
   - See your top 5 restaurants

## Data Fetching

The bot always fetches fresh data when you click "Update Order Data":

1. **Fresh Data**: The update process:
   - Logs into TGO Yemek using credentials from your `.env` file
   - Fetches your most current order history
   - Saves it as JSON
   - Converts it to CSV for analysis

2. **Manual**: You can also manually fetch data:
   ```
   python login_flow.py
   ```

## Advanced AI Recommendations

The bot offers two types of recommendations:
- **Standard recommendations** based on simple pattern analysis
- **Advanced AI recommendations** powered by Claude AI that provide deeper insights

To use the Claude AI feature:
1. Add your Anthropic API key to the `.env` file
2. Click the "🤖 AI Recommendation" button in the bot

You can customize the AI recommendations by editing the `claude_prompt_template.txt` file, which contains the instructions sent to Claude AI. This allows you to tailor the AI's analysis to focus on aspects you're most interested in.

## Security

- All credentials (Telegram, TGO Yemek, and Claude API) are stored in the `.env` file
- This file is not tracked by git (listed in .gitignore)
- Never share your .env file or hardcode credentials in your scripts

## License

MIT 