import requests
import re
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Send request to the login page without cookies to get the CSRF token
def get_csrf_token():
    print("Step 1: Getting CSRF token from login page...")
    
    url = "https://tgoyemek.com/giris"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://tgoyemek.com/"
    }
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Send request without cookies
    response = session.get(url, headers=headers)
    
    print(f"Status code: {response.status_code}")
    
    # Check if we received the response with the login form
    if response.status_code == 200:
        # Save the HTML response for examination
        with open('login_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Response saved to login_page.html")
        
        # Extract cookies from the response
        cookies = session.cookies.get_dict()
        
        print(f"Cookies received from login page: {json.dumps(cookies, indent=2)}")
        
        # Get CSRF token from API
        csrf_response = session.get("https://tgoyemek.com/api/auth/csrf", cookies=cookies)
        
        if csrf_response.status_code == 200:
            try:
                csrf_data = csrf_response.json()
                csrf_token = csrf_data.get("csrfToken")
                print(f"CSRF token obtained: {csrf_token}")
                
                # Add the CSRF token to cookies
                cookies["tgo-csrf-token"] = csrf_token
                
                return csrf_token, cookies, session
            except Exception as e:
                print(f"Error parsing CSRF response: {str(e)}")
        else:
            print(f"Failed to get CSRF token. Status: {csrf_response.status_code}")
    
    print("Could not obtain necessary tokens")
    return None, None, None

# Step 2: Send login request with the CSRF token
def login(csrf_token, cookies, session):
    print("\nStep 2: Attempting login with the CSRF token and cookies...")
    
    # Get login credentials from environment variables
    tgo_username = os.getenv("TGO_USERNAME")
    tgo_password = os.getenv("TGO_PASSWORD")
    
    # Check if credentials are available
    if not tgo_username or not tgo_password:
        print("Error: TGO_USERNAME or TGO_PASSWORD not found in .env file.")
        print("Please add your TGO Yemek credentials to your .env file:")
        print("TGO_USERNAME=your_email@example.com")
        print("TGO_PASSWORD=your_password")
        return None, None
    
    url = "https://tgoyemek.com/api/auth/login"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://tgoyemek.com",
        "Referer": "https://tgoyemek.com/giris",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    # Prepare login payload with the CSRF token
    payload = {
        "csrfToken": csrf_token,
        "password": tgo_password,
        "username": tgo_username
    }
    
    # Log the payload we're using (but mask the password)
    masked_payload = {
        "csrfToken": csrf_token,
        "password": "********",
        "username": tgo_username
    }
    print(f"Login payload: {json.dumps(masked_payload, indent=2)}")
    
    # Send login request with cookies and payload
    response = session.post(url, headers=headers, json=payload)
    
    print(f"Login status code: {response.status_code}")
    
    # Try to parse the response
    try:
        response_json = response.json()
        print(f"Login response: {json.dumps(response_json, indent=2)}")
        
        # Check for specific error messages
        if response.status_code == 403:
            if "errorDetails" in response_json:
                error_msg = response_json["errorDetails"][0].get("errorMessage", "")
                if "Beklenmeyen bir hata" in error_msg:
                    print("Error suggests trying again or refreshing the page")
                    
                    # Let's try another API endpoint format
                    print("\nAttempting alternative login endpoint...")
                    alt_url = "https://tgoyemek.com/api/auth/signin"
                    alt_response = session.post(alt_url, headers=headers, json=payload)
                    
                    print(f"Alternative login status code: {alt_response.status_code}")
                    try:
                        alt_json = alt_response.json()
                        print(f"Alternative login response: {json.dumps(alt_json, indent=2)}")
                    except:
                        print(f"Alternative login response (text): {alt_response.text[:500]}...")
    except:
        print(f"Login response (text): {response.text[:500]}...")
    
    # Save cookies for future use
    with open('login_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(session.cookies.get_dict(), f, indent=2)
    
    print("Login cookies saved to login_cookies.json")
    
    return response, response_json if 'response_json' in locals() else None

# Step 3: Fetch orders from the API
def fetch_orders(session, auth_data):
    print("\nStep 3: Fetching orders from API...")
    
    # Check if we have the access token
    if not auth_data or 'access_token' not in auth_data:
        print("No access token available. Cannot fetch orders.")
        return None
    
    access_token = auth_data['access_token']
    
    url = "https://api.tgoapis.com/web-checkout-apicheckout-santral/orders"
    params = {
        "page": 1,
        "pageSize": 50
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://tgoyemek.com",
        "Referer": "https://tgoyemek.com/",
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"Using authorization: Bearer {access_token[:20]}...")
    
    # Send request to get orders
    response = session.get(url, headers=headers, params=params)
    
    print(f"Orders API status code: {response.status_code}")
    
    # Handle the response
    if response.status_code == 200:
        try:
            orders_data = response.json()
            # Save to file
            with open('orders_data.json', 'w', encoding='utf-8') as f:
                json.dump(orders_data, f, indent=2, ensure_ascii=False)
            
            print("Orders data saved to orders_data.json")
            
            # Print in pretty format
            print("\nOrders Data:")
            print(json.dumps(orders_data, indent=2, ensure_ascii=False))
            
            return orders_data
        except Exception as e:
            print(f"Error parsing orders response: {str(e)}")
            print(f"Response text: {response.text[:500]}...")
    else:
        print(f"Failed to fetch orders. Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Response text: {response.text[:500]}...")
    
    return None

# Main execution
if __name__ == "__main__":
    try:
        # Step 1: Get CSRF token
        csrf_token, cookies, session = get_csrf_token()
        
        if csrf_token and cookies and session:
            # Add a delay to simulate human behavior
            time.sleep(1)
            
            # Step 2: Login with the token
            login_response, auth_data = login(csrf_token, cookies, session)
            
            # Add a delay before fetching orders
            time.sleep(1)
            
            # Step 3: Fetch orders
            orders_data = fetch_orders(session, auth_data)
        else:
            print("Failed to extract necessary tokens. Cannot proceed with login.")
    except Exception as e:
        print(f"An error occurred: {str(e)}") 