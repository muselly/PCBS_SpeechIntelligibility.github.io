import expyriment as xpy
import os
from scipy.io import wavfile
import glob
from os import listdir
import numpy as np
import scipy.signal as sp
from scipy.fftpack import fft, ifft
import math
from playsound import playsound

cutOff_freq = 2000
pathToRaw = './snd/rawDigits/'
pathToDigits = './snd/digits/'

# Signal Processing functions
def filterSignal(s, cutOff_freq, btype, sf):
    """Takes a signal and applies a Butterwoth filter to it. btype: 'lowpass’ or ‘highpass’"""
    nyquist = sf/2
    wc = cutOff_freq / nyquist
    b, a = sp.butter(6, wc, btype = btype)
    return sp.lfilter(b, a, s)

def rms(signal):
    """Returns the rms level of the signal."""
    sumofsquares = 0
    for v in signal:
        sumofsquares = sumofsquares + v**2
    mean_sumofsquares = sumofsquares / len(signal)
    return math.sqrt(mean_sumofsquares)

def filterSignal(s, cutOff_freq, btype, sf):
    """Takes a signal and applies a Butterwoth filter to it. btype: 'lowpass’ or ‘highpass’"""
    nyquist = sf/2
    wc = cutOff_freq / nyquist
    b, a = sp.butter(6, wc, btype = btype)
    return sp.lfilter(b, a, s)

def rms(signal):
    """Returns the rms level of the signal."""
    sumofsquares = 0
    for v in signal:
        sumofsquares = sumofsquares + v**2
    mean_sumofsquares = sumofsquares / len(signal)
    return math.sqrt(mean_sumofsquares)

def SSN(signals, sf):
    """Computes 30sec of Speech Shaped Noise for a list of speech signals of the same length
    by randomizing the phases of the FFTs of each signal.
    Returns the speech shaped noise signal."""

    add_sec = 29 # seconds to add to the final noise

    lmax = max([len(s) for s in signals])
    signals = [np.pad(s, (0, lmax-len(s) + add_sec * sf), mode = 'constant') for s in signals]
    signals = np.stack(signals)

    # Sum the FFT spectrums of each signal
    ss_fft = fft(signals).sum(axis = 0)

    # Randomize phase
    ss_fft = ss_fft * np.exp(1j * 2 * np.pi * np.random.rand(*ss_fft.shape))

    ssn_s = ifft(ss_fft).real
    ssn_s = filterSignal(ssn_s, 8000, 'lowpass', sf)
    return ssn_s

def random_ssn(ssn, sf):
    """Randomly pick out 3 seconds of speech shaped noise from the original 30 second long SSN."""
    short_ssn_len = sf * 3 # triplet digit presentation is 3 seconds long
    start = np.random.randint(0, len(ssn) - short_ssn_len)
    end = start + short_ssn_len
    short_ssn = ssn[start : end]
    return short_ssn

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

# Main: Creating stimulus
# From raw wav recordings of each digit, get an array of signals of equal length and rewrite them to wav files
digits_files = listdir(pathToRaw)

# Make a dictionary wtih each digit recording: key = name of file, value = array of signal
digits = {}
for file in digits_files:
    sf, s = wavfile.read(pathToRaw + file)
    digits[file] = s

# Pad the signal arrays to make them all equal length
lmax = max([len(s) for s in digits.values()])
for file in digits:
    digits[file] = np.pad(digits[file], (0, lmax-len(digits[file])), mode = 'constant')

# Equalize the Root Mean Squared amplitude of the recordings
rms_max = max([rms(s) for s in digits.values()])
for file in digits:
    digits[file] = digits[file]/rms(digits[file]) * rms_max

# Write processed digit signals file
for file, snd in digits.items():
    snd.astype(float)
    wavfile.write(pathToDigits + 'post_' + file, sf, snd)

#Make a speech shaped noise out of them and write it to file
ssn = SSN(digits.values(), sf)
rms_ssn = rms(ssn)
wavfile.write('./snd/SSN/speech_shaped_noise.wav', sf, ssn)

# Creating all filter (x2) and SNR (x5) conditions for each digit
pathToStimuli = './snd/SIN/'
conds_SNR = [0, -3, -6, -9, -12]
conds_freq = [0, 1] # 0 : 'lowpass', 1: 'highpass'

# 300 trials (2x5 conditions, 30 trials each) + 9 practice trials
n_practice = 9
n_trials_condition = 3 # must be a multiple of 3
n_trials_total = n_trials_condition * len(conds_SNR) * len(conds_freq)
n_blocks = 3
n_trials_block = int(n_trials_total/n_blocks)

stim = np.empty((n_trials_total, 3*sf)) # array to store auditory stimuli (each stimulus is 3 seconds long)
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
            filt = 'highpass'
        else:
            filt = 'lowpass'

        # generate random triplet digits for each condition
        # (so that each digit is presented the same number of times in each condition)
        triplets = generate_triplets(n_trials_condition)

        # One triplet will be presented on each trial
        for triplet in triplets:
            # Create signal for trial
            stimulus = np.concatenate(([digits[str(triplet[0]) + '.wav'], digits[str(triplet[1]) + '.wav'], digits[str(triplet[2]) + '.wav']]), axis = 0)
            # Extract noise for trials
            trial_ssn = random_ssn(ssn, sf)

            # Filter stim according to freq condition
            s = filterSignal(stimulus, cutOff_freq, filt, sf = sf)

            # Fix SNR
            # fixing rms level of signal relative to speech shaped noise
            x = 10**(-r/10)
            s = s/rms(s) * rms(trial_ssn)/x
            # Adding noise to signal
            s = s + trial_ssn

            # fill arrays to store trial data
            stim[random_order[t]] = s
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
instructions_trial_respond = "Please type the digits you have heard in the order you heard them (eg: '123'). Do not separate them by any character. \n \
If you have not heard a digit, type a '0' in place of that digit (eg: '103'). \n \
Press ENTER to move to submit your response and move to the next trial."

# EXPERIMENT

#Create an experiment object
exp = xpy.design.Experiment(name = "Speech Intelligibility Task")

# Comment for real experiment
#xpy.control.set_develop_mode(on=True)

#initialize experiment object
xpy.control.initialize(exp)

exp.add_data_variable_names(['Block', 'Trial', 'Responses', 'Score', 'Filter', 'SNR'])

# Running the actual experiment:
xpy.control.start(exp, skip_ready_screen = True)

xpy.stimuli.TextScreen('Digit Triplet Recognition Task', instructions_gen).present()
xpy.io.Keyboard().wait(keys = xpy.misc.constants.K_SPACE) #to wait for space to be pressed

for block in range (n_blocks):
    for trial in range(n_trials_block):
        t = trial + block * n_trials_block
        stimulus = stim[t]
        wavfile.write('stim.wav', sf, stimulus)

        xpy.stimuli.TextLine(instructions_trial_snd).present()

        exp.clock.wait(100)

        playsound('stim.wav')

        xpy.stimuli.TextLine(text = instructions_trial_respond).present()

        # Take input response from user
        input = xpy.io.TextInput(message=instructions_trial_respond, \
        length=3,user_text_bold=True, user_text_colour=(255,255,255))
        response = input.get()

        # Transform input response in an array of integers
        response = [int(response[0]), int(response[1]), int(response[2])]

        # Compare to correct response to score
        correct_digits = correct_responses[t]
        score = 0
        for i in range(len(response)):
            d = response[i]
            correct_d = correct_digits[i]
            if d == correct_d:
                score = score + 1

        block_id = block + 1
        t= t+1
        trialSNR = stim_snr[t]
        if stim_freq[t]:
            trialFilter = 'highpass'
        else:
            trialFilter = 'lowpass'

        # Store all the trial information in the output file
        exp.data.add([block_id, t, correct_digits, response, score, trialFilter, trialSNR])

    if block < n_blocks - 1:
        xpy.stimuli.TextScreen('End of block.', 'Press SPACEBAR to start new block.').present()
        xpy.io.Keyboard().wait(keys = xpy.misc.constants.K_SPACE) #to wait for space to be pressed
    elif block == n_blocks - 1:
        xpy.stimuli.TextScreen('End of experiment. Thank you for participating!').present()
        xpy.io.Keyboard().wait()

xpy.control.end(exp)
