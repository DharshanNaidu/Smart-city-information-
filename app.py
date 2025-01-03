from flask import Flask, request, jsonify
import openai
import json

app = Flask(__name__)

openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your OpenAI API key

# Load data files
def load_data(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {file_name}.")
        return {}

# Load data
transport_data = load_data("transport_data.json")
utility_data = load_data("utility_data.json")
events_data = load_data("events_data.json")

# Define functions
def get_transport_info(route):
    if route in transport_data.get("routes", {}):
        info = transport_data["routes"][route]
        return f"Next bus for route '{route}' is at {info['next_bus']} from {info['stop']} on {info['date']}."
    return "No data available for this route."

def get_utility_status(utility, area):
    utility_info = utility_data.get(utility, [])
    for entry in utility_info:
        if entry["area"].lower() == area.lower():
            return f"{utility.capitalize()} status in {area}: {entry['status']}."
    return f"No data available for {utility} in {area}."

def get_events_on_date(date):
    events = [event for event in events_data if event["date"] == date]
    if events:
        return "Events on " + date + ":\n" + "\n".join(f"- {event['name']} at {event['location']}" for event in events)
    return f"No events found for {date}."

def query_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a smart city information chatbot."},
                      {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error interacting with OpenAI API: {e}"

# API Routes
@app.route('/api/query', methods=['POST'])
def handle_query():
    user_input = request.json.get('query')
    
    if "bus" in user_input.lower():
        route = request.json.get('route')
        response = get_transport_info(route)
    elif "electricity" in user_input.lower() or "water" in user_input.lower():
        utility = "electricity" if "electricity" in user_input.lower() else "water"
        area = request.json.get('area')
        response = get_utility_status(utility, area)
    elif "event" in user_input.lower():
        date = request.json.get('date')
        response = get_events_on_date(date)
    else:
        response = query_openai(user_input)

    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
