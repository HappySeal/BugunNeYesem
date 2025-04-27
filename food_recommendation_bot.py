import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
import csv
from collections import Counter
import datetime
import random
import subprocess

# Import functions from our existing scripts
import parse_orders
import food_recommendation_simple
import food_recommendation  # Import the Claude AI version
import login_flow  # Import login flow script for fetching data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get API key from environment variables
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

if not TELEGRAM_API_KEY:
    logger.error("No TELEGRAM_API_KEY found in .env file")
    print("Error: TELEGRAM_API_KEY not found in .env file.")
    print("Please create a .env file with your Telegram Bot API key like:")
    print("TELEGRAM_API_KEY=your_bot_token_here")
    exit(1)

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Helper function to create the main menu
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📋 View Order History')
    btn2 = types.KeyboardButton('🔮 Get Food Recommendation')
    btn3 = types.KeyboardButton('🔄 Update Order Data')
    btn4 = types.KeyboardButton('🍔 Top 5 Restaurants')
    btn5 = types.KeyboardButton('🤖 AI Recommendation')
    btn6 = types.KeyboardButton('ℹ️ About')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# Start command handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Welcome to Food Recommendation Bot!*\n\n"
        "I can help you analyze your food ordering history from TGO Yemek and provide personalized recommendations.\n\n"
        "What would you like to do?"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="Markdown",
        reply_markup=create_main_menu()
    )

# Handle button clicks and messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '📋 View Order History':
        show_order_history(message)
    elif message.text == '🔮 Get Food Recommendation':
        send_food_recommendation(message)
    elif message.text == '🔄 Update Order Data':
        update_order_data(message)
    elif message.text == '🍔 Top 5 Restaurants':
        show_top_restaurants(message)
    elif message.text == '🤖 AI Recommendation':
        send_claude_ai_recommendation(message)
    elif message.text == 'ℹ️ About':
        send_about_info(message)
    else:
        bot.reply_to(
            message, 
            "I don't understand that command. Please use the menu options.",
            reply_markup=create_main_menu()
        )

# Function to show order history
def show_order_history(message):
    csv_file = "orders_summary.csv"
    
    if not os.path.exists(csv_file):
        bot.send_message(
            message.chat.id,
            "No order history found. Please update order data first."
        )
        return
    
    # Read the first 10 orders to show
    orders = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            orders.append(row)
            if len(orders) >= 10:
                break
    
    if not orders:
        bot.send_message(
            message.chat.id,
            "Your order history is empty."
        )
        return
    
    # Format the message
    history_text = "📋 *Your Recent Orders:*\n\n"
    for i, order in enumerate(orders, 1):
        history_text += (
            f"{i}. *{order['Item Name']}*\n"
            f"   🍽️ {order['Restaurant Name']} ({order['Restaurant Location']})\n"
            f"   📅 {order['Date']} at {order['Time']}\n"
            f"   💰 {order['Price (TL)']} TL\n"
            f"   📌 Status: {order['Status']}\n\n"
        )
    
    # Split message if it's too long for Telegram
    if len(history_text) > 4000:
        chunks = [history_text[i:i+4000] for i in range(0, len(history_text), 4000)]
        for chunk in chunks:
            bot.send_message(message.chat.id, chunk, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, history_text, parse_mode="Markdown")

# Function to send food recommendation
def send_food_recommendation(message):
    csv_file = "orders_summary.csv"
    
    if not os.path.exists(csv_file):
        bot.send_message(
            message.chat.id,
            "No order history found. Please update order data first."
        )
        return
    
    # Show typing action while generating recommendation
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Get orders and analysis
    orders = food_recommendation_simple.read_order_history(csv_file)
    if not orders:
        bot.send_message(
            message.chat.id,
            "Error reading order history."
        )
        return
    
    analysis = food_recommendation_simple.analyze_orders(orders)
    recommendation = food_recommendation_simple.generate_recommendation(analysis)
    
    # Send recommendation
    bot.send_message(
        message.chat.id,
        f"🔮 *Food Recommendation Based on Your Order History*\n\n{recommendation}",
        parse_mode="Markdown"
    )

# Function to send Claude AI food recommendation
def send_claude_ai_recommendation(message):
    csv_file = "orders_summary.csv"
    
    if not os.path.exists(csv_file):
        bot.send_message(
            message.chat.id,
            "No order history found. Please update order data first."
        )
        return
    
    # Check if Claude API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        bot.send_message(
            message.chat.id,
            "⚠️ Claude AI API key not found in .env file.\n\n"
            "To use AI recommendations, please add your Anthropic API key to the .env file:\n"
            "ANTHROPIC_API_KEY=your_api_key_here\n\n"
            "You can get an API key from https://console.anthropic.com/"
        )
        return
    
    # Show typing action to indicate processing
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Send initial message
    processing_msg = bot.send_message(
        message.chat.id,
        "🤖 *Asking Claude AI for recommendations...*\n"
        "This might take a moment as we analyze your order patterns.",
        parse_mode="Markdown"
    )
    
    # Get orders from CSV
    orders = food_recommendation.read_order_history(csv_file)
    if not orders:
        bot.edit_message_text(
            "Error reading order history.",
            message.chat.id,
            processing_msg.message_id
        )
        return
    
    # Get Claude AI recommendation
    recommendation = food_recommendation.get_food_recommendation(orders)
    
    if recommendation:
        # Save recommendation to file for future reference
        with open("claude_recommendation.txt", "w", encoding="utf-8") as f:
            f.write(recommendation)
        
        # Send as a new message (Claude responses can be long)
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Send with header
        header = "🤖 *Claude AI Food Recommendation Analysis*\n\n"
        
        # Split message if it's too long for Telegram
        if len(header + recommendation) > 4000:
            bot.send_message(
                message.chat.id,
                header,
                parse_mode="Markdown"
            )
            
            # Send chunks of the recommendation
            chunks = [recommendation[i:i+4000] for i in range(0, len(recommendation), 4000)]
            for chunk in chunks:
                bot.send_message(message.chat.id, chunk)
        else:
            bot.send_message(
                message.chat.id,
                header + recommendation,
                parse_mode="Markdown"
            )
        
        # Add a follow-up message
        bot.send_message(
            message.chat.id,
            "The full recommendation has also been saved to claude_recommendation.txt"
        )
    else:
        bot.edit_message_text(
            "❌ Failed to get recommendations from Claude AI.\n"
            "Please check your API key or try again later.",
            message.chat.id,
            processing_msg.message_id
        )

# Function to update order data
def update_order_data(message):
    bot.send_message(
        message.chat.id,
        "🔄 Starting to update order data..."
    )
    
    # Show typing action
    bot.send_chat_action(message.chat.id, 'typing')
    
    json_file = "orders_data.json"
    csv_file = "orders_summary.csv"
    
    # Always fetch fresh data from TGO Yemek
    bot.send_message(
        message.chat.id,
        "📥 Fetching fresh data from TGO Yemek..."
    )
    
    # Try to fetch data using login_flow
    try:
        bot.send_message(
            message.chat.id,
            "🔑 Logging in to TGO Yemek..."
        )
        
        # Step 1: Get CSRF token
        csrf_token, cookies, session = login_flow.get_csrf_token()
        
        if not csrf_token or not cookies or not session:
            bot.send_message(
                message.chat.id,
                "❌ Failed to get CSRF token from TGO Yemek. Please check your network connection."
            )
            return
        
        bot.send_message(
            message.chat.id,
            "✅ CSRF token obtained. Attempting login..."
        )
        
        # Step 2: Login with the token
        login_response, auth_data = login_flow.login(csrf_token, cookies, session)
        
        if not auth_data or 'access_token' not in auth_data:
            bot.send_message(
                message.chat.id,
                "❌ Login failed. Please check your TGO credentials in the .env file."
            )
            return
        
        bot.send_message(
            message.chat.id,
            "✅ Login successful. Fetching order data..."
        )
        
        # Step 3: Fetch orders
        orders_data = login_flow.fetch_orders(session, auth_data)
        
        if not orders_data:
            bot.send_message(
                message.chat.id,
                "❌ Failed to fetch order data."
            )
            return
        
        bot.send_message(
            message.chat.id,
            f"✅ Successfully fetched fresh order data from TGO Yemek and saved to {json_file}."
        )
        
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Error fetching data: {str(e)}\n\nPlease check your network connection and TGO credentials in the .env file."
        )
        return
    
    # Now process the JSON file to CSV
    try:
        # Process the file using our parsing function
        output_file = parse_orders.parse_orders_to_csv(json_file, csv_file)
        bot.send_message(
            message.chat.id,
            f"✅ Order data updated successfully!\nSaved to: {output_file}\n\nYou can now view your order history and get recommendations."
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Error updating order data: {str(e)}"
        )

# Function to show top restaurants
def show_top_restaurants(message):
    csv_file = "orders_summary.csv"
    
    if not os.path.exists(csv_file):
        bot.send_message(
            message.chat.id,
            "No order history found. Please update order data first."
        )
        return
    
    # Read order history
    restaurants = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            restaurant_name = row['Restaurant Name']
            location = row['Restaurant Location']
            # Create a unique identifier for the restaurant
            restaurant_id = f"{restaurant_name} ({location})"
            restaurants.append(restaurant_id)
    
    # Count occurrences of each restaurant
    counter = Counter(restaurants)
    top_5 = counter.most_common(5)
    
    if not top_5:
        bot.send_message(
            message.chat.id,
            "No restaurant data found."
        )
        return
    
    # Format the message
    top_text = "🍔 *Your Top 5 Restaurants:*\n\n"
    for i, (restaurant, count) in enumerate(top_5, 1):
        top_text += f"{i}. *{restaurant}*\n   Ordered {count} time{'s' if count > 1 else ''}\n\n"
    
    bot.send_message(message.chat.id, top_text, parse_mode="Markdown")

# Function to send about information
def send_about_info(message):
    about_text = (
        "ℹ️ *About Food Recommendation Bot*\n\n"
        "This bot analyzes your food ordering history from TGO Yemek and provides personalized recommendations.\n\n"
        "It parses order data from JSON format, analyzes your preferences, and suggests what you might want to order today based on your past behavior.\n\n"
        "For even more personalized recommendations, try the '🤖 AI Recommendation' option which uses Claude AI to provide deeper insights.\n\n"
        "Created with ❤️ using Python and TeleBot."
    )
    bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

# Main function
def main():
    logger.info("Starting bot...")
    print("Starting Food Recommendation Bot...")
    
    # Check if order data exists, if not prompt to update
    csv_file = "orders_summary.csv"
    if not os.path.exists(csv_file):
        print("Order data not found. You may need to update order data when the bot starts.")
    
    # Start the bot
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 