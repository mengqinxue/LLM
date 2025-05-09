import re
import ollama

# Simulated database
bookings = {}

# Helper function to call Ollama model
def call_model(prompt):
    response = ollama.generate(model="deepseek-r1:1.5b", prompt=prompt)
    return response['response'].strip()

# Determine user intent
def determine_intent(user_input):
    prompt = f"""
                You are an AI assistant specialized in hotel bookings. Only respond to queries related to booking, 
                modifying, or canceling reservations. If the query is unrelated, reply with "I can only assist with 
                booking, modifying, or canceling hotel reservations."

                Classify the following input:
                "{user_input}"

                Respond in this format:
                Intent: [booking/modify/cancel/unrelated]
                """

    response = call_model(prompt)

    pattern = r'<think>.*?</think>'
    response = re.sub(pattern, '', response, flags=re.DOTALL).strip()

    if response.startswith("Intent:"):
        return response.split(":")[1].strip()
    return "unrelated"

# Get name and check-in date
def get_user_info():
    name = input("Please provide your name: ").strip()
    date = input("Please provide your check-in date (YYYY-MM-DD): ").strip()
    return name, date

# Main agent loop
def main():
    print("Welcome to Hotel Booking Assistant. I can help with booking, modifying, or canceling your reservation.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        intent = determine_intent(user_input)

        if intent == "unrelated":
            print("\nAssistant: I can only assist with booking, modifying, or canceling hotel reservations.")
            continue

        print("\nAssistant: Could you please provide your name and check-in date?")
        name, date = get_user_info()

        key = (name.lower(), date)

        if intent == "booking":
            if key in bookings:
                print(f"\nAssistant: You already have a booking for {date}.")
            else:
                bookings[key] = {"status": "confirmed"}
                print(f"\nAssistant: Thank you, {name}. Your booking for {date} has been confirmed.")

        elif intent == "modify":
            if key not in bookings:
                print(f"\nAssistant: No booking found for {name} on {date}.")
            else:
                new_date = input("Please provide the new check-in date (YYYY-MM-DD): ").strip()
                del bookings[key]
                new_key = (name.lower(), new_date)
                bookings[new_key] = {"status": "modified"}
                print(f"\nAssistant: Your booking has been updated to {new_date}.")

        elif intent == "cancel":
            if key not in bookings:
                print(f"\nAssistant: No booking found for {name} on {date}.")
            else:
                del bookings[key]
                print(f"\nAssistant: Your booking for {date} has been canceled.")

if __name__ == "__main__":
    main()