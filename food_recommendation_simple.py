import csv
import os
import datetime
import random
from collections import Counter

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

def analyze_orders(orders):
    """Analyze order patterns and preferences"""
    
    # Extract item names, times, and prices
    item_names = [order['Item Name'] for order in orders]
    times = [order['Time'] for order in orders]
    prices = [float(order['Price (TL)']) for order in orders]
    
    # Calculate most ordered items
    item_counter = Counter(item_names)
    most_common_items = item_counter.most_common(3)
    
    # Calculate average ordering time
    time_hours = []
    for time_str in times:
        try:
            hour = int(time_str.split(':')[0])
            time_hours.append(hour)
        except (ValueError, IndexError):
            pass
    
    avg_hour = sum(time_hours) / len(time_hours) if time_hours else None
    
    # Calculate price range
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0
    
    # Check if user prefers burgers, fast food, etc.
    food_types = {
        'burger': ['Burger', 'King', 'Secret'],
        'pizza': ['Pizza'],
        'sandwich': ['Sandwich', 'SANDWİCH', 'Tost'],
        'tacos': ['Tacos'],
        'chicken': ['Chicken', 'Tavuk'],
        'coffee': ['Latte', 'Caffe']
    }
    
    type_counts = {food_type: 0 for food_type in food_types}
    
    for item in item_names:
        for food_type, keywords in food_types.items():
            if any(keyword in item for keyword in keywords):
                type_counts[food_type] += 1
    
    # Sort by count
    preferred_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'most_common_items': most_common_items,
        'avg_hour': avg_hour,
        'price_range': (min_price, max_price, avg_price),
        'preferred_types': preferred_types
    }

def generate_recommendation(analysis):
    """Generate food recommendations based on analysis"""
    
    recommendations = []
    
    # Current time
    now = datetime.datetime.now()
    current_hour = now.hour
    current_day = now.strftime('%A')
    
    # 1. What to order today
    if analysis['most_common_items']:
        favorite = analysis['most_common_items'][0][0]
        recommendations.append(f"1. TODAY'S RECOMMENDATION:\n"
                              f"Based on your ordering history, you might enjoy ordering {favorite} again. "
                              f"It's your most frequently ordered item.")
    
    # 2. New restaurant or food type to try
    preferred_type = analysis['preferred_types'][0][0] if analysis['preferred_types'] else None
    
    # Suggestions based on preferred type
    new_suggestions = {
        'burger': ['Smash Burger', 'Gourmet Burger', 'Vegetarian Burger', 'Lokma Burger'],
        'pizza': ['Neapolitan Pizza', 'Chicago Deep Dish', 'New York Style Pizza', 'Turkish Pide'],
        'sandwich': ['Cuban Sandwich', 'Banh Mi', 'Club Sandwich', 'Pastrami Sandwich'],
        'tacos': ['Birria Tacos', 'Fish Tacos', 'Korean Fusion Tacos', 'Breakfast Tacos'],
        'chicken': ['Korean Fried Chicken', 'Nashville Hot Chicken', 'Rotisserie Chicken', 'Chicken Tikka'],
        'coffee': ['Specialty Pour Over', 'Cold Brew', 'Turkish Coffee', 'Flat White']
    }
    
    if preferred_type and preferred_type in new_suggestions:
        suggestions = new_suggestions[preferred_type]
        suggestion = random.choice(suggestions)
        recommendations.append(f"2. NEW RECOMMENDATION:\n"
                              f"Since you enjoy {preferred_type}, you might like to try {suggestion}. "
                              f"It's a different take on your preferred food type.")
    else:
        recommendations.append("2. NEW RECOMMENDATION:\n"
                              "You might enjoy trying Turkish cuisine like Iskender Kebab or Manti (Turkish dumplings).")
    
    # 3. Typical ordering time
    if analysis['avg_hour']:
        hour = int(analysis['avg_hour'])
        hour_str = f"{hour}:00" if hour < 10 else f"{hour}:00"
        recommendations.append(f"3. ORDERING PATTERN:\n"
                              f"You typically order food around {hour_str}. "
                              f"{'That\'s coming up soon!' if abs(current_hour - hour) <= 2 else 'Plan ahead for your usual mealtime.'}")
    
    # 4. Patterns and preferences
    min_price, max_price, avg_price = analysis['price_range']
    
    if avg_price > 0:
        recommendations.append(f"4. SPENDING PATTERNS:\n"
                              f"Your orders usually range from {min_price:.2f} TL to {max_price:.2f} TL, "
                              f"with an average of {avg_price:.2f} TL per order.\n")
    
    # Add food type preferences
    type_insights = []
    for food_type, count in analysis['preferred_types']:
        if count > 0:
            type_insights.append(f"{food_type} ({count} orders)")
    
    if type_insights:
        recommendations.append(f"FOOD PREFERENCES:\n"
                              f"Your favorite food types appear to be: {', '.join(type_insights[:3])}")
    
    # Day-specific recommendation
    if current_day in ['Saturday', 'Sunday']:
        recommendations.append("WEEKEND SPECIAL:\n"
                              "Since it's the weekend, consider treating yourself to something more upscale "
                              "or a relaxed brunch option!")
    
    return "\n\n".join(recommendations)

def main():
    csv_file = "orders_summary.csv"
    
    # Read order history from CSV
    orders = read_order_history(csv_file)
    if not orders:
        return
    
    # Analyze order patterns
    analysis = analyze_orders(orders)
    
    # Generate recommendations
    recommendation = generate_recommendation(analysis)
    
    # Display and save recommendations
    print("\n===== FOOD RECOMMENDATIONS =====\n")
    print(recommendation)
    
    # Save recommendation to file
    with open("food_recommendation.txt", "w", encoding="utf-8") as f:
        f.write(recommendation)
    
    print("\nRecommendation saved to food_recommendation.txt")

if __name__ == "__main__":
    main() 