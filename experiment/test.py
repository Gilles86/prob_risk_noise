from psychopy import visual, core
# Set visual backend

win = visual.Window(size=[800, 600], color='black')

stim = visual.TextStim(win, text='Hello', color=(1, .5, 1))  # No explicit colorSpace

stim.draw()
win.flip()
core.wait(1)
win.close()