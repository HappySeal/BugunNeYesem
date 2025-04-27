import csv
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_order_history(csv_file):
    """Read the order history from CSV file"""
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run parse_orders.py first.")
        return None
    
    orders = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            orders.append(row)
    
    print(f"Loaded {len(orders)} orders from {csv_file}")
    return orders

def get_food_recommendation(orders):
    """Get food recommendation from Claude AI based on order history"""
    
    # Use Claude API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file.")
        print("Please create a .env file with your Anthropic API key like:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        return None
    
    # Prepare the API request data
    api_url = "https://api.anthropic.com/v1/messages"
    
    # Load the prompt template
    try:
        with open('claude_prompt_template.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("Warning: claude_prompt_template.txt not found. Using default prompt.")
        prompt_template = """Here's my food order history:

{order_history}

Based on my order history, can you suggest:
1. What I might want to order today
2. A new restaurant or food type I might enjoy trying
3. What time I typically order food
4. Any patterns or preferences you notice in my ordering habits

Please be specific in your recommendations and explain your reasoning."""
    
    # Format the order history for Claude
    order_history_text = ""
    for order in orders[:20]:  # Limit to the 20 most recent orders
        order_history_text += f"- {order['Item Name']} from {order['Restaurant Name']} ({order['Restaurant Location']}) ordered on {order['Date']} at {order['Time']} for {order['Price (TL)']} TL\n"
    
    # Create the final prompt by substituting the order history into the template
    prompt = prompt_template.replace("{order_history}", order_history_text)
    
    # Log what prompt is being used (for debugging)
    print(f"Using Claude prompt with {len(orders[:20])} orders")
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    print("Sending request to Claude AI...")
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        recommendation = result["content"][0]["text"]
        
        return recommendation
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Claude API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def main():
    csv_file = "orders_summary.csv"
    
    # Read order history from CSV
    orders = read_order_history(csv_file)
    if not orders:
        return
    
    # Get food recommendation from Claude AI
    recommendation = get_food_recommendation(orders)
    
    if recommendation:
        print("\n===== CLAUDE'S FOOD RECOMMENDATIONS =====\n")
        print(recommendation)
        
        # Save recommendation to file
        with open("food_recommendation.txt", "w", encoding="utf-8") as f:
            f.write(recommendation)
        
        print("\nRecommendation saved to food_recommendation.txt")
    else:
        print("Failed to get recommendation from Claude AI.")
        print("Check your API key and internet connection.")

if __name__ == "__main__":
    main() 