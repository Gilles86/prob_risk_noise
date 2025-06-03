from psychopy import visual, core, monitors, event

# Define a monitor with known specifications
mon = monitors.Monitor(name='testMonitor', width=30, distance=50)  # Width in cm, distance in cm

# Create a window with this monitor
win = visual.Window([1200, 1200], monitor=mon, units='deg')

# Import the RangeResponseSlider (ensure it is correctly implemented in stimuli.py)
from stimuli import RangeResponseSlider, DiscreteResponseSlider

# Initialize the response slider
response_slider = DiscreteResponseSlider(
    win,
    position=(0, 0),  # Centered
    length=15,  # Length in degrees
    height=1.,  # Height in degrees
    color=[.5, .5, .5],
    borderColor=[1, 1, 1],
    borderWidth=1.,
    range=(0, 60),  # Slider range
    markerColor=[0.25, 0.25, 0.25],
    marker_position=3,
    n_discrete_steps=6,
    slider_type='natural',
)

# Create a mouse object
mouse = event.Mouse(win=win)

# Draw slider
response_slider.draw()
win.flip()

# Timer for tracking response time
clock = core.Clock()
response_onset = None
last_mouse_pos = mouse.getPos()[0]

# Response loop
while clock.getTime() < 50.0:  # Adjusted based on your original `core.wait(50.0)`
    current_mouse_pos = mouse.getPos()[0]
    
    # Update marker position if mouse moves significantly
    if abs(last_mouse_pos - current_mouse_pos) > 0.05:  # Threshold for movement
        marker_position = response_slider.mouseToMarkerPosition(current_mouse_pos)
        response_slider.setMarkerPosition(marker_position)
        response_slider.show_marker = True
        last_mouse_pos = current_mouse_pos

    # If mouse button is clicked, register response time and position
    if mouse.getPressed()[0]:  # Left mouse button
        response_onset = clock.getTime()
        response_time = response_onset  # Since the trial starts at time 0
        response_value = response_slider.marker_position
        print(f"Response time: {response_time:.3f}s, Response: {response_value}")
        break  # Exit loop after response

    # Redraw and update display
    response_slider.draw()
    win.flip()

# Close the window properly
win.close()
