# ScheduleMaster

## Overview

The ScheduleMaster Chatbot is a Streamlit-based application that allows users to interact with the Cal.com API for scheduling and listing events. The chatbot leverages OpenAI's GPT-4 model to process user inputs and perform tasks such as creating new events and retrieving scheduled events based on user email.

## Features

- **Create New Events**: Schedule new events if the desired time slot is available.
- **List Scheduled Events**: Retrieve and display scheduled events based on the user's(technically meeting attendee) email.
- I plan to implement more Features such as update and delete bookings.

**Instructions:**

- Replace `eventTypeId` in the `create_event` and `check_slot_availability` function with the ID (an integer) of the event you want to schedule at line numbers 65 and 120 in main.py file.
- Make sure you have the packages openai, Json, requests, and Streamlit.
- There will be only one input field in the UI. If the chatbot requests additional details for a prompt, please provide them along with the prompt because the chatbot has no memory feature for now.
- Make sure you have the **OpenAI** and **CalCom** APIs exported in environment variables.

## Usage

1. **Run the Streamlit application**:

   ```bash
   streamlit run main.py
   ```
2. **Interact with the chatbot**:

   - Enter your query in the input box and press "Send".
   - The chatbot will respond based on the input and perform the requested actions.
   - Example conversations are in outputs folder

###### *Example conversations are in outputs folder*
