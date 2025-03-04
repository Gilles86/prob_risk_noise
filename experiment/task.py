import argparse
import os.path as op
from psychopy.visual import Slider
from psychopy import event
from exptools2.core import PylinkEyetrackerSession, Trial
from utils import _create_stimulus_array, get_output_dir_str, DummyWaiterTrial, OutroTrial, get_settings
from instruction import InstructionTrial
from stimuli import FixationLines, ResponseSlider, ProbabilityPieChart
import numpy as np
import logging
from psychopy.visual import Line, Rect, TextStim

class ProbCueTrial(InstructionTrial):

    def __init__(self, session, trial_nr, prob, **kwargs):

        txt = session.instructions['prob_cue'].format(prob=int(prob*100))
        bottom_txt = ""

        self.prob_cue = ProbabilityPieChart(session.win,
                                            prob,
                                            session.settings['prob_cue'].get('cue_size'),
                                            pos=(0, -1.))

        super().__init__(session, trial_nr, txt, bottom_txt=bottom_txt,
                        phase_durations=[session.settings['durations']['cue_trials']],
                         **kwargs)

        self.text.pos = (0, 1.)

    def draw(self):
        super().draw()
        self.prob_cue.draw()

    def get_events(self):
        Trial.get_events(self)


class TaskTrial(Trial):
    def __init__(self, session, trial_nr, phase_durations=None,
                jitter=1,
                payoff=15, prob=0.55, **kwargs):

        if phase_durations is None:
            phase_durations = [session.settings['durations']['first_fixation'], # Red fixation
                               session.settings['durations']['second_fixation'],# Pie chart
                            session.settings['durations']['array_duration'],    # Doy display
                            jitter,                                 # ISI            
                            session.settings['durations']['response_screen'], # Response
                            session.settings['durations']['feedback'], # Feedback
                            0.0] #Spillover

        self.total_duration = np.sum(phase_durations)

        self.stimulus_phase = [2]
        self.response_phase = 4
        self.feedback_phase = 5

        phase_names = ['fixation1', 'prob_cue', 'stimulus', 'jitter', 'response', 'feedback', 'iti']

        super().__init__(session, trial_nr, phase_durations, phase_names=phase_names, **kwargs)

        self.parameters['prob'] = prob
        self.parameters['payoff'] = payoff
        self.parameters['jitter'] = jitter
        self.stimulus_array = _create_stimulus_array(self.session.win, self.parameters['payoff'],
                                                     self.session.settings['cloud'].get('aperture_radius'),
                                                     self.session.settings['cloud'].get('dot_radius'),)

        self.prob_cue = ProbabilityPieChart(self.session.win, self.parameters['prob'],
                                            self.session.settings['prob_cue'].get('fixation_size'),
                                            include_text=False)

        if self.session.settings['task'].get('show_prob_during_payoff'):
            self.prob_fixation = ProbabilityPieChart(self.session.win, self.parameters['prob'],
                                                self.session.settings['prob_cue'].get('fixation_size'),
                                                include_text=False)


        self.parameters['start_marker_position'] = np.random.randint(self.session.settings['slider']['range'][0],
                                                                     self.session.settings['slider']['range'][1] + 1)

    def get_events(self):

        events = super().get_events()

        response_slider = self.session.response_slider

        if self.phase == (self.response_phase - 1):

            if (not self.session.mouse.getPressed()[0]) and (self.session.mouse.getPos()[0] != response_slider.marker.pos[0]):
                try:
                    self.session.mouse.setPos((response_slider.marker.pos[0],0))
                    self.last_mouse_pos = response_slider.marker.pos[0]
                except Exception as e:
                    print(e)

            self.last_mouse_pos = self.session.mouse.getPos()[0]/self.session.settings['interface']['mouse_multiplier']

        elif self.phase == self.response_phase:

            if not hasattr(self, 'response_onset'):
                current_mouse_pos = self.session.mouse.getPos()[0]/self.session.settings['interface']['mouse_multiplier']
                if np.abs(self.last_mouse_pos - current_mouse_pos) > response_slider.delta_rating_deg:
                    marker_position = response_slider.mouseToMarkerPosition(current_mouse_pos)
                    response_slider.setMarkerPosition(marker_position)
                    self.last_mouse_pos  = current_mouse_pos
                    response_slider.show_marker = True
                
                if self.session.mouse.getPressed()[0]:
                    self.response_onset = self.session.clock.getTime()
                    self.parameters['response_time'] = self.response_onset - self.session.global_log.iloc[-1]['onset']
                    self.parameters['response'] = response_slider.marker_position

                    time_so_far = self.session.clock.getTime() - self.start_trial
                    self.phase_durations[6] = self.total_duration - time_so_far - self.phase_durations[5]
                    self.stop_phase()

        super().get_events()

    def draw(self):

        if self.session.win.mouseVisible:
            self.session.win.mouseVisible = False

        if (self.phase == self.feedback_phase) & (not hasattr(self, 'response_onset')):
            self.session.fixation_lines.draw(draw_fixation_cross=False)
        elif self.phase in self.stimulus_phase:
            self.session.fixation_lines.draw(draw_fixation_cross=False)
        else:
            self.session.fixation_lines.draw()

        response_slider = self.session.response_slider

        if self.phase == 0: # Fixation
            self.session.fixation_lines.setColor((-1, .5, -1), fixation_cross_only=True)
        elif self.phase == 1: # Prob cue
            self.session.fixation_lines.setColor((1, -1, -1), fixation_cross_only=True)
            self.prob_cue.draw()
        elif self.phase in self.stimulus_phase:

            if self.session.settings['task'].get('show_prob_during_payoff'):
                self.prob_fixation.draw()

            self.stimulus_array.draw()

        elif self.phase == (self.response_phase - 1):
            response_slider.setMarkerPosition(self.parameters['start_marker_position'])
            response_slider.show_marker = False

        elif self.phase == self.response_phase:
            response_slider.marker.inner_color = self.session.settings['slider'].get('color')
            response_slider.draw()

        elif self.phase == self.feedback_phase:
            if hasattr(self, 'response_onset'):
                response_slider.marker.inner_color = self.session.settings['slider'].get('feedbackColor')
                response_slider.draw()
            else:
                self.session.too_late_stimulus.draw()
                    
        self.previous_phase = self.phase

def main(subject, session, run, range, settings='default', calibrate_eyetracker=False):
    from session import WTPSession
    output_dir, output_str = get_output_dir_str(subject, session, 'estimation_task', run)
    settings_fn, use_eyetracker = get_settings(settings)

    session = WTPSession(output_str=output_str, subject=subject,
                          output_dir=output_dir, settings_file=settings_fn, 
                          run=run, eyetracker_on=use_eyetracker,
                          calibrate_eyetracker=calibrate_eyetracker)

    session.create_trials()
    session.run()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('subject', type=str, help='Subject nr')
    argparser.add_argument('session', type=str, help='Session')
    argparser.add_argument('run', type=int, help='Run')
    argparser.add_argument('--settings', type=str, help='Settings label', default='default')
    argparser.add_argument('--calibrate_eyetracker', action='store_true', dest='calibrate_eyetracker')

    args = argparser.parse_args()

    main(args.subject, args.session, args.run, args.settings, calibrate_eyetracker=args.calibrate_eyetracker)