import json
import csv
import os

def parse_orders_to_csv(json_file, csv_file):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create CSV file
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        
        # Write header
        csv_writer.writerow(['Item Name', 'Restaurant Name', 'Restaurant Location', 'Date', 'Time', 'Price (TL)', 'Status'])
        
        # Process each order
        for order in data.get('orders', []):
            # Extract item name
            item_name = order.get('product', {}).get('name', 'Unknown')
            
            # Extract restaurant info
            restaurant = order.get('store', {})
            restaurant_name = restaurant.get('name', 'Unknown')
            
            # Extract location from restaurant name if available (usually in parentheses)
            restaurant_location = 'Unknown'
            if '(' in restaurant_name and ')' in restaurant_name:
                start_idx = restaurant_name.find('(')
                end_idx = restaurant_name.find(')')
                if start_idx < end_idx:
                    restaurant_location = restaurant_name[start_idx+1:end_idx].strip()
                    # Clean up restaurant name by removing the location part
                    restaurant_name = restaurant_name[:start_idx].strip()
            
            # Extract date and time
            order_date = order.get('orderDate', '')
            date_parts = order_date.split(' / ')
            date = date_parts[0] if len(date_parts) > 0 else ''
            time = date_parts[1] if len(date_parts) > 1 else ''
            
            # Extract price
            price = order.get('price', {}).get('totalPrice', 0)
            
            # Extract status
            status_text = order.get('status', {}).get('statusText', '')
            
            # Write to CSV
            csv_writer.writerow([item_name, restaurant_name, restaurant_location, date, time, price, status_text])
    
    print(f"CSV file created successfully: {csv_file}")
    return csv_file

if __name__ == "__main__":
    # Input and output file paths
    json_file = "orders_data.json"
    csv_file = "orders_summary.csv"
    
    # Check if the input file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found. Please make sure the file exists.")
    else:
        # Process the file
        output_file = parse_orders_to_csv(json_file, csv_file)
        print(f"Orders have been exported to {output_file}") 