import requests
import sys
import json
import time

# Telegram bot settings
telegram_token = '7184477916:AAH5b9ofeWi_ybx9K43l-pp0MGz-IEuwCT8'
telegram_chat_id = '-1002192418490'
# Zelenka API endpoint for threads
url = "https://api.zelenka.guru/threads?forum_id=8&order=thread_create_date_reverse"

headers = {
    "accept": "application/json",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOjYyNzkzLCJpc3MiOiJsenQiLCJleHAiOjAsImlhdCI6MTcyMDc3ODkyNCwianRpIjo2MTA0NjIsInNjb3BlIjoiYmFzaWMgcmVhZCBwb3N0IGNvbnZlcnNhdGUifQ.PNEHsnrwguj-PlkEaLvqpcOOVRq-w0GQ3Poc83IcCaKPD-rFgWbGItty7G3O9d3eTehrk6PaQ9xXvymKrynR2281ZARrCqzCG7hYNDidIoYjwcm_8Solf_QP9SCjf1QvR5LUqbEr8510dUSqOtjTyQ9PXLrrHqrAqV0vYFO7RQY"
}
def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    params = {"chat_id": telegram_chat_id, "text": message}
    response = requests.get(telegram_url, params=params)
    return response.json()

## Initialize list to store previous threads
latest_thread_date = None

def get_latest_threads():
    global latest_thread_date
    try:
        # Make the API request
        response = requests.get(url, headers=headers)
        
        # Check if request was successful
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse JSON response
        data = response.json()
        
        # Check if 'threads' key exists in the response
        if 'threads' in data:
            # Extract threads from response
            threads = data['threads']
            
            if threads:
                # Get the most recent thread_create_date
                threads.sort(key=lambda x: x['thread_create_date'], reverse=True)
                current_latest_thread_date = threads[0]['thread_create_date']
                
                # If it's the first scan, initialize latest_thread_date
                if latest_thread_date is None:
                    latest_thread_date = current_latest_thread_date
                
                # Process new threads
                new_threads = [thread for thread in threads if thread['thread_create_date'] > latest_thread_date]
                if new_threads:
                    for thread in new_threads:
                        title = thread.get('thread_title', '')
                        permalink = thread.get('links', {}).get('permalink', '')
                        message = f"New thread: {title}\nLink: {permalink}"
                        send_telegram_message(message)
                        print(f"Sent Telegram notification: {message}")
                    
                    # Update the latest thread date to the newest one
                    latest_thread_date = current_latest_thread_date
        else:
            print("No 'threads' key found in API response")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {str(e)}")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {str(e)}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

while True:
    get_latest_threads()
    # Sleep for 10 seconds before polling again
    time.sleep(10)