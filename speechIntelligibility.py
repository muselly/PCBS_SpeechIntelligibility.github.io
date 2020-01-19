import expyriment as xpy
import os
from scipy.io import wavfile
import glob
from os import listdir
from scipy.io import wavfile
import numpy as np

# Experimental Conditions
conds_SNR = [0, -3, -6, -9, -12]
conds_freq = [0,1] # 0 : 'lowpass', 1 : 'highpass'

# 300 trials (2x5 conditions, 30 trials each) + 9 practice trials
n_practice = 9
durations = 10000
n_trials_condition = 30
n_trials_total = n_trials_condition * len(conds_SNR) * len(conds_freq)
n_blocks = 5
n_trials_block = int(n_trials_total/n_blocks)


# Stimuli
def generate_triplets(numTrials):
    """Generate digit triplets for numTrials number of trials.
    Each digit is presented the same number of times.
    Outputs an array of triplet arrays.
    To be generated for each participant."""
    n = numTrials*3/9
    digits = np.array(range(9)) + 1
    stimuli_set = np.repeat(digits, n)
    stimuli_rand = np.random.choice(stimuli_set, size = len(stimuli_set), replace = False)
    stimuli_triplets = stimuli_rand.reshape((-1, 3))
    return stimuli_triplets

sf = 44100
pathToStimuli = './snd/SIN/'
stimuli = np.empty((n_trials_total, 3*sf)) # array to store auditory stimuli (each stimulus is 3 seconds long)
correct_responses = np.empty((n_trials_total, 3)) # array to store correct responses fro each trial
stim_snr = np.empty(n_trials_total) # array to store SNR condition for each trial
stim_freq = np.empty(n_trials_total) # array to store frequency condition for each trial

# Array to keep track of the randomization of the stimuli
random_order = np.random.choice(np.array(range(n_trials_total)), size = n_trials_total, replace = False)

# Generate stimulus sequence in random order and corresponding correct_responses
t=0 #trial counter
for freq in conds_freq:
    for r in conds_SNR:
        if freq:
            filter = 'highpass'
        else:
            filter = 'lowpass'
        pathToStim = './snd/SIN/' + filter + '/' + str(r) + '/'
        stim_names = listdir(pathToStim)
        digits = list(range(10))

        # Load each digit file as a signal array
        for file in stim_names:
            digit = int(file[0])
            sf, s = wavfile.read(pathToStim + file)
            digits[digit] = s

        # generate random triplet digits for each condition
        # (so that each digit is presented the same number of times in each condition)
        triplets = generate_triplets(n_trials_condition)

        # One triplet will be presented on each trial
        for triplet in triplets:
            stimulus = np.concatenate(([digits[triplet[0]], digits[triplet[1]], digits[triplet[2]]]), axis = 0)
            # Setting correpct responses, SNR condition and frequency condition information for each trial.
            stimuli[random_order[t]] = stimulus
            correct_responses[random_order[t]] = triplet
            stim_snr[random_order[t]] = r
            stim_freq[random_order[t]] = freq
            t = t + 1


#Instructions
instructions_gen = "On each trial, you will be presented with three auditory recordings of digits (any number from 1 to 9). \n \
Please input the digits you hear in the response box. \n \
If you do not recognized a digit, type a '0' in place of that digit.\n \
Press SPACEBAR to start."
instructions_trial_snd = "Listen to the three presented digits."
intrcution_trial_respond = "Please type the digits you have heard in the order you heard them (eg: '123'). Do not separate them by any character. \n \
If you have not heard a digit, type a '0' in place of that digit (eg: '103'). \n \
Press ENTER to move to submit your response and move to the next trial."

#Create an experiment object
exp = xpy.design.Experiment(name = "Speech Intelligibility Task")

# Comment for real experiment
xpy.control.set_develop_mode(on=True)

#initialize experiment object
xpy.control.initialize(exp)

for block in range(n_blocks):
    temp_block = xpy.design.Block(name = str(block + 1))

    for trial in range(n_trials_block):
        # Trial count is done on total range of trials, regardless of blocks.
        t = trial + block * n_trials_block

        filename = 'stim.wav'
        curr_stim = stimuli[t]
        wavfile.write(filename, sf, curr_stim)

        temp_stim = xpy.stimuli.Audio(filename = filename)
        # temp_stim = xpy.stimuli.TextLine(text = 'To replace audio')

        temp_trial = xpy.design.Trial()

        temp_trial.add_stimulus(temp_stim)

        if stim_freq[t]:
            trialFilter = 'highpass'
        else:
            trialFilter = 'lowpass'

        trialSNR = stim_snr[t]

        temp_trial.set_factor('Filter', trialFilter)
        temp_trial.set_factor('SNR', trialSNR)

        temp_block.add_trial(temp_trial)

    exp.add_block(temp_block)

exp.data_variable_names = ['Block', 'Trial', 'Responses', 'Score', 'Filter', 'SNR']


# Running the actual experiment:
xpy.control.start(exp, skip_ready_screen = True)

xpy.stimuli.TextScreen('Digit Triplet Recognition Task', instructions_gen).present()
xpy.io.Keyboard().wait(keys = xpy.misc.constants.K_SPACE) #to wait for space to be pressed

for block in exp.blocks:
    for trial in block.trials:
        xpy.stimuli.TextScreen(heading = 'Block' + block.name, text = instructions_trial_snd).present()
        trial.stimuli[0].preload()

        #present stimulus
        if xpy.stimuli.Audio.is_preloaded():
            trial.stimuli[0].present()

        xpy.control.wait_end_audiosystem() # Wait for the sound to finish playing
        xpy.stimuli.TextLine(text = instructions_trial_snd).present()

        # Take input response from user
        input = xpy.io.TextInput(message='Enter the three heard digits:', \
        length=3,user_text_bold=True, user_text_colour=(255,255,255))
        response = input.get()

        exp.keyboard.wait(keys = xpy.misc.constants.K_KP_ENTER)

        # Transform input response in an array of integers
        response = [int(response[0]), int(response[1]), int(response[2])]

        # Compare to correct response to score
        correct_digits = correct_responses[trial.id]
        score = 0
        for i in range(len(response)):
            d = response[i]
            correct_d = correct_digits[i]
            if d == correct_d:
                score = score + 1

        # Store allt the trial information in the output file
        exp.data.add([block.name, trial.id, reponse, score, trial.get_factor('trialFilter'), trial.get_factor('trialSNR')])

    if block.name != n_blocks:
        xpy.stimuli.TextScreen("Short break", "That was block:" + block.name + "\n Press SPACEBAR to start next block.").present()
        xpy.io.Keyboard.wait(xpy.misc.constants.K_SPACE) #to wait for space to be pressed

xpy.control.end(exp)
