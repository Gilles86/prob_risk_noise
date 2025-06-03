from session import WTPSession
from task import TwoSliderTasktrial

session = WTPSession(
    output_str='test_slider2',
    subject='test',
    run=1,
    settings_file='settings/default.yml',
    eyetracker_on=False,
    slider_type='two-sliders',
)


trial = TwoSliderTasktrial(session,
                           1,
                           )
session.trials = [trial]
session.run()