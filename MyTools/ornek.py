from osiloskop import Osiloskop

# Create an instance
osc = Osiloskop()

# Start streaming
osc.start_stream()

# Get microphone data
data = osc.get_data()

# Send data (if needed)
processed_data = osc.send_data()

# Visualize
osc.visualize()
