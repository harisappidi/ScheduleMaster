from openai import OpenAI
import json
import requests
import os
import streamlit as st


OpenAI.api_key = os.getenv("OPENAI_API_KEY")
CALCOM_API_KEY = os.getenv("CALCOM_API_KEY")

client = OpenAI()

main_placeholder = st.empty()

# Function to retrieve the scheduled events of an user based on email
def list_events(email):
    """
    Retrieve the scheduled events of a user based on their email.

    Args:
        email (str): The user's email address.

    Returns:
        str: A JSON string containing the scheduled events or an error message.
    """
    main_placeholder.text("Checking for scheduled events....✅✅✅")

    url = "https://api.cal.com/v1/bookings" 
    params = {
        "attendeeEmail": email,
        "apiKey": CALCOM_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        events = response.json()
        return json.dumps(events)
    except Exception as err:
        return json.dumps({"error": "An unexpected error occurred", "details": str(err)})

# Function to check the availability of an user
def check_slot_availability(date, time, timezone):
    """
    Check the availability of a time slot on a given date.

    Args:
        date (str): The date in YYYY-MM-DD format.
        time (str): The time in HH:MM format.
        timezone (str): The time zone in IANA format.

    Returns:
        tuple: A tuple containing a boolean indicating availability and the formatted slot time.
    """
    main_placeholder.text("Checking for Slot availability....✅✅✅")

    url = "https://api.cal.com/v1/slots"

    date_from = f'{date}T00:00:00.000Z'
    date_to = f'{date}T23:45:00.000Z'

    # Replace "eventTypeId" for the event you want to schedule
    params = {
        "apiKey": CALCOM_API_KEY,
        "startTime": date_from,
        "eventTypeId": 885994,
        "endTime": date_to,
        "timeZone": timezone
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        available_slots = response.json().get('slots', {}).get(date, [])
        list_of_available_slots = [list(slot.values()) for slot in available_slots]

        user_requested_slot_time = f'{date}T{time}:00{list_of_available_slots[0][0][-6:]}'
        main_placeholder.empty()

        if [user_requested_slot_time] in list_of_available_slots:
            return True, user_requested_slot_time, None
        else:
            return False, user_requested_slot_time, "The requested slot is unavailable."
    except requests.exceptions.HTTPError as http_err:
        main_placeholder.empty()
        return False, None, f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        main_placeholder.empty()
        return False, None, f"Request exception: {req_err}"
    except Exception as err:
        main_placeholder.empty()
        return False, None, f"An unexpected error occurred: {err}"
    
# Function to create a new event
def create_event(date, time, reason, timezone):
    """
    Create a new event if the requested slot is available.

    Args:
        date (str): The date in YYYY-MM-DD format.
        time (str): The time in HH:MM format.
        reason (str): The reason for the event.
        timezone (str): The time zone in IANA format.

    Returns:
        str: A JSON string containing the booking confirmation or an error message.
    """

    availability, formatted_slot_time, error = check_slot_availability(date, time, timezone)

    if availability:
        main_placeholder.text("Slot is available. Let me book the event....✅✅✅")

        url = f"https://api.cal.com/v1/bookings?apiKey={CALCOM_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        # Replace "eventTypeId" for the event you want to schedule
        body = {
            "eventTypeId": 885994,
            "start": formatted_slot_time,
            "responses": {
                "name": "John Doe",
                "email": "johndoe@test.com",
                "location": {
                    "value": "integrations:calcom",
                    "optionValue": ""
                }
            },
            "metadata": {},
            "timeZone": timezone,
            "language": 'en',
            "title": reason,
            "status": "ACCEPTED",
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            return json.dumps(response.json())
        except requests.exceptions.HTTPError as http_err:
            return json.dumps({"error": "HTTP error occurred", "details": str(http_err)})
        except requests.exceptions.RequestException as req_err:
            return json.dumps({"error": "Request exception", "details": str(req_err)})
        except Exception as err:
            return json.dumps({"error": "An unexpected error occurred", "details": str(err)})
    else:
        return json.dumps({"message": error})

# Function_calls to run the conversation with the user
def run_conversation(user_input):
    """
    Run the conversation with the user, calling the appropriate functions based on the user's input.

    Args:
        user_input (str): The input from the user.

    Returns:
        str: The response from the assistant.
    """
    messages = [{"role": "user", "content": user_input}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_event",
                "description": "Create a new event, do not assume any of the parameters provided, ask the user for the missing parameters. The date and time must be provided in YYYY-MM-DD and HH:MM format respectively. Relative terms like 'tomorrow' are not accepted and do not provide any suggestions on dates. The time should be in HH:MM format. Ask user to append the parameters to their input.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "The date must be provided in YYYY-MM-DD format."},
                        "time": {"type": "string", "description": "The time of the event in HH:MM format"},
                        "reason": {"type": "string", "description": "The event reason"},
                        "timezone": {"type": "string", "description": "The time zone of Attendee in IANA format. Eg: America/New_York"},
                    },
                    "required": ["date", "time", "reason", "timezone"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_events",
                "description": "List scheduled events, asks user to append the email to their input if email is not provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "The user's email"},
                    },
                    "required": ["email"],
                },
            },
        },
    ]
    
    # Step #1: Prompt with content that may result in function call.
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
        )
    response_observed = response.choices[0].message

    response_message = response_observed.content

    tool_calls = response_observed.tool_calls
    
    # Step 2: Check if the model wanted to call at least one function
    if tool_calls: 
        available_functions = {
            "create_event": create_event,
            "list_events": list_events,
        }
        # extend conversation with assistant's reply
        messages.append(response_observed)
        
        # Step 3: Call the function and append the results to the messages list
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
        
            try:
                function_response = function_to_call(**function_args)
            except Exception as err:
                function_response = json.dumps({"error": "Function call failed", "details": str(err)})

            main_placeholder.text("Assistant is analyzing the data....✅✅✅")
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call.id, 
                "name": function_name, 
                "content":function_response
            })

        # Step 4: Invoke the chat completions API with the function response appended to the messages list
        model_response_with_function_call = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        response_message = model_response_with_function_call.choices[0].message.content
        main_placeholder.text("Assistant processed the request....✅✅✅")
        return response_message
    else:
        main_placeholder.text("Assistant needs additional Information....✅✅✅")
        return response_message

def main():
    """Main function to run the Streamlit application."""
    st.title("Calcom Chatbot")
    st.write("This is a chatbot that can help you schedule events and list your scheduled events.")

    user_input = st.text_input("User: ")

    if st.button("Send"):
        with st.spinner("Processing..."):
            llm_response = run_conversation(user_input)
        st.write(f"Assistant: {llm_response}")

if __name__ == "__main__":
    main()