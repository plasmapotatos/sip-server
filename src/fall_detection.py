import time

# Function to simulate fall detection loop
def fall_detection_simulation():
    try:
        # Initial loop - no fall detected
        for _ in range(5):
            print("No fall detected.")
            time.sleep(1)

        # Fall detected
        print("\nFall detected: Planning Actions...")
        time.sleep(2)
        
        # Simulate audio transcription
        print("\nTranscription: \"Oh my god, he fell! His head hit the floor really hard. Someone get help!\"")
        time.sleep(3)

        # First set of actions to be taken
        actions = [
            {'action': 'speak', 'message': 'Are you okay? Help is on the way.', 'desiredVolume': '5'},
            {'action': 'listen_for_feedback'}
        ]

        # Output the first set of actions
        for action in actions:
            print("\nAction:")
            for key, value in action.items():
                print(f"{key.capitalize()}: {value}")
            time.sleep(1)
        
        # Listening for feedback
        print("\nListening for feedback...")
        time.sleep(3)

        # Simulate second audio transcription
        print("\nTranscription: \"Call and text his emergency contact!\"")
        time.sleep(2)

        # Second set of actions to be taken
        emergency_contact_number = "6692524341"
        actions = [
            {'action': 'call', 'number': emergency_contact_number},
            {'action': 'sms', 'number': emergency_contact_number, 'message': 'Emergency detected. Immediate assistance required.'},
            {'action': 'listen_for_feedback'}
        ]

        # Output the second set of actions
        for action in actions:
            print("\nAction:")
            for key, value in action.items():
                print(f"{key.capitalize()}: {value}")
            time.sleep(1)

        # Final feedback listening loop
        while True:
            print("\nListening for feedback...")
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted.")

# Run the fall detection simulation
fall_detection_simulation()
