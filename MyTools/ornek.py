from osiloskop import Osiloskop

# Create and start stream
osc = Osiloskop()
osc.start_stream()

# Visualize non-blockingly
osc.visualize()

# You can continue executing code here
print("Continuing with other tasks...")

# Later, process data
raw_data = osc.get_data()
filtered_data = osc.apply_bandpass_filter(raw_data, 20, 2000)
dom_freq = osc.estimate_dominant_frequency(filtered_data)
