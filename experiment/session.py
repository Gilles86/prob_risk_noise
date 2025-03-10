from exptools2.core import PylinkEyetrackerSession, Trial
from psychopy import event
from stimuli import ResponseSlider, FixationLines, TextStim, RangeResponseSlider
import yaml
import os.path as op
from instruction import InstructionTrial
from task import TaskTrial, OutroTrial, DummyWaiterTrial, ProbCueTrial, TwoStageTasktrial
import numpy as np

class WTPSession(PylinkEyetrackerSession):
    def __init__(self, output_str, subject=None, output_dir=None, settings_file=None, run=None, eyetracker_on=False, calibrate_eyetracker=False,
                 slider_type='natural'):

        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file, eyetracker_on=eyetracker_on)

        self.show_eyetracker_calibration = calibrate_eyetracker

        self.mouse = event.Mouse(visible=False)

        self.instructions = yaml.safe_load(open(op.join(op.dirname(__file__), 'instruction_texts.yml'), 'r'))

        self.settings['subject'] = subject
        self.settings['run'] = run

        self.fixation_lines = FixationLines(self.win,
                                            self.settings['cloud'].get('aperture_radius'),
                                            color=(1, -1, -1),
                                            **self.settings['fixation_lines'])
        self.too_late_stimulus = TextStim(self.win, text='Too late!', pos=(0, 0), color=(1, -1, -1), height=0.5)

        self.slider_type = slider_type
        self._setup_response_slider(slider_type=slider_type)

        print("Window colorSpace:", self.win.colorSpace)


    def _setup_response_slider(self, slider_type='natural'):

        position_slider = (0, 0)
        length_line = self.settings['slider'].get('max_length')

        if slider_type in ['natural', 'log']:
            self.response_slider = ResponseSlider(self.win,
                                            position_slider,
                                            length_line,
                                            self.settings['slider'].get('height'),
                                            self.settings['slider'].get('color'),
                                            self.settings['slider'].get('borderColor'),
                                            self.settings['slider'].get('range'),
                                            marker_position=None,
                                            markerColor=self.settings['slider'].get('markerColor'),
                                            borderWidth=self.settings['slider'].get('borderWidth'),
                                            text_height=self.settings['slider'].get('text_height'),
                                            slider_type=slider_type)
        elif slider_type == 'two-stage':

            width_proportion = self.settings['slider'].get('width_proportion', 0.10)

            self.response_slider1 = RangeResponseSlider(self.win,
                                            position_slider,
                                            length_line,
                                            self.settings['slider'].get('height'),
                                            self.settings['slider'].get('color'),
                                            self.settings['slider'].get('borderColor'),
                                            self.settings['slider'].get('range'),
                                            marker_position=None,
                                            markerColor=self.settings['slider'].get('markerColor'),
                                            borderWidth=self.settings['slider'].get('borderWidth'),
                                            text_height=self.settings['slider'].get('text_height'),
                                            slider_type='natural',
                                            width_proportion=width_proportion,
                                            )


            self.response_slider2 = ResponseSlider(self.win,
                                            position_slider,
                                            length_line,
                                            self.settings['slider'].get('height'),
                                            self.settings['slider'].get('color'),
                                            self.settings['slider'].get('borderColor'),
                                            self.settings['slider'].get('range'),
                                            show_number=True,
                                            marker_position=None,
                                            markerColor=self.settings['slider'].get('markerColor'),
                                            borderWidth=self.settings['slider'].get('borderWidth'),
                                            text_height=self.settings['slider'].get('text_height'),
                                            slider_type='natural')


    def run(self):
        """ Runs experiment. """
        if self.eyetracker_on and self.show_eyetracker_calibration:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        for trial in self.trials:
            trial.run()

        self.close()

    def create_trials(self, include_instructions=True):
        """Create trials."""

        instruction_trial1 = InstructionTrial(self, 0, self.instructions['instruction1'].format(run=self.settings['run']))
        dummy_trial = DummyWaiterTrial(self, 0, n_triggers=self.settings['mri']['n_dummy_scans'])
        
        self.trials = [instruction_trial1, dummy_trial]

        if not include_instructions:
            self.trials = self.trials[1:]

        n_trials = self.settings['task'].get('n_trials')
        n_probs = len(self.settings['task'].get('probabilities'))
        n_payoffs = len(self.settings['task']['payoffs'])

        # Make sure n_trials is a multiple of 6 and 4 (or throw error)
        if n_trials % n_probs != 0:
            raise ValueError('n_trials should be a multiple of n_probs')
        if n_trials % n_payoffs != 0:
            raise ValueError('n_trials should be a multiple of n_payoffs')

        probs = list(self.settings['task']['probabilities'])
        np.random.shuffle(probs)

        payoffs_ = list(self.settings['task']['payoffs'])


        trial_nr = 1

        possible_isis = self.settings['durations'].get('isi')
        isis = possible_isis * int(np.ceil(n_trials / len(possible_isis)))
        isis = isis[:n_trials]

        for prob in probs:
            self.trials.append(ProbCueTrial(self, -1, prob))

            np.random.shuffle(payoffs_)

            for payoff in payoffs_:
                
                if self.slider_type == 'two-stage':
                    self.trials.append(TwoStageTasktrial(self, trial_nr, jitter=isis[trial_nr-1], payoff=payoff,
                                             prob=prob))
                else:
                    self.trials.append(TaskTrial(self, trial_nr, jitter=isis[trial_nr-1], payoff=payoff,
                                                prob=prob))
                trial_nr += 1

        self.trials.append(OutroTrial(session=self))
