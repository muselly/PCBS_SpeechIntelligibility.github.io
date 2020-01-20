# PCBS Project - Speech Intelligibility Frequency Importance Function
##  Eléonore Scholler

### Main Goal
The main goal of this project is to program a task to determine the relative importance of higher (above 2kHz) versus lower (below 2kHz) frequencies on speech intelligibility. Creating the stimuli involves speech signal processing resulting is varying signal-to-noise ratios (SNR) using braodband speech shaped noise (SSN) on narrowband digit triplets in French. The program will collect participant input digits (what they hear) and score their response. Finally, it'll determine the relative importance of higher versus lower frequencies for speech recognition for each participant. The entire project will be done in Python and the final output will be published on a GitHub webpage.

### Sound Materials
The speech material includes recordings of the nine digits in French, each one second long. On each trial, a triplet of digits in noise will be presented. 
I will be recording and cleaning these digit recordings.  
In this project, I will first be generating speech shaped noise based on these sentences which will be added to the sentence recordings at random phases in order to create 5 SNR conditions: 0, -3, -6, -9, -12 dB SNR (calculated using RMS amplitude of signal). In order to determine the importance of each frequency band, there will be two frequency conditions: high frequency SNR (hi) and low frequency SNR (lo). This will therefore involve lowpass and highpass filtering (de Cheveigné & Nelken, 2019).
Each sentence will be randomly assigned to a SNR and frequency condition. 


```json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import IPython.display as ipd
from scipy.io import wavfile
import scipy.signal as sp
from scipy.fftpack import fft, ifft
import math
from os import listdir

# Setting up
plt.rcParams["figure.figsize"] = (14,4)
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
    """Computes Speech Shaped Noise for a list of speech signals of the same length
    by randomizing the phases of the FFTs of each signal.
    Returns the speech shaped noise signal."""

    lmax = max([len(s) for s in signals])
    signals = [np.pad(s, (0, lmax-len(s)), mode = 'constant') for s in signals]
    signals = np.stack(signals)

    # Sum the FFT spectrums of each signal
    ss_fft = fft(signals).sum(axis = 0)

    # Randomize phase
    ss_fft = ss_fft * np.exp(1j * 2 * np.pi * np.random.rand(*ss_fft.shape))

    ssn_s = ifft(ss_fft).real
    ssn_s = filterSignal(ssn_s, 8000, 'lowpass', sf)
    return ssn_s


# Visualization Functions

def plot_fft(s, sf):
    """Computes the fft and shows its spectrum."""
    # number of samples
    N = len(s)
    # sampling spacing
    T = 1/sf

    # taken from https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
    yf = fft(s)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.show()

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
plot_fft(ssn, sf)

# Creating all filter (x2) and SNR (x5) conditions for each digit
pathToStimuli = './snd/SIN/'
SNR_conds = [0, -3, -6, -9, -12]
freq_conds = ['lowpass', 'highpass']
hi_stim = np.empty((5,10,lmax))
lo_stim = np.empty_like(hi_stim)
# loop through each digit recording (x9)
for file, snd in digits.items():
    # Extract the digit from filename
    digit = int(file[0])

    # loop through conditions (x2)
    for i in range(len(freq_conds)):
        freq = freq_conds[i]
        s = filterSignal(snd, cutOff_freq, freq, sf = sf)

        # loop through Signal to Noise ration conditions (x5)
        for j in range(len(SNR_conds)):
            r = SNR_conds[j]
            # fixing rms level of signal relative to speech shaped noise
            x = 10**(-r/10)
            s = s/rms(s) * rms_ssn/x
            # Adding noise to signal
            stim = s + ssn

            wavfile.write(pathToStimuli + freq + '/' +  str(r) + '/' + file, sf, stim)

            # Store signals in output arrays
            if freq == 'lowpass':
                lo_stim[j][digit] = stim
            elif freq == 'highpass':
                hi_stim[j][digit] = stim

```

### Task
Each digit triplet will be played once to the subject. The subject will then be asked to type what they heard before moving on to the next triplet.
There will be 9 practice trials in order to learn the task, and 300 test sentences (30 for each frequency and SNR condition). If the participant doesn't know what digit was presented, they must input a '0' instead. The subject will not be given any feedback. 

The task has been programmed on experyment, but due to technical problems using the `experyment.stimuli.Audio` class, the stimuli do not play (I haven't been able to find anyone else with the same problem online either). 

```json
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

```

### Data Analysis
**Sentence scoring**: each correct digit will be assigned one point. '0' responses will not be assigned any points. 
For each subject, speech intelligibility (scores) will be plotted in terms of SNR for each frequency condition, and the SNR value for 50% speech intelligibility will be extracted and compared between frequency conditions. I expect that higher frequencies will be more important to speech intelligibility than lower frquencies, but the final goal of this manipulation is to compare individual variability in terms of the relative importance given to each frequency band. 

### References
de Cheveigné, A., & Nelken, I. (2019). Filters: when, why, and how (not) to use them. Neuron, 102(2), 280-293.  
DePaolis, R. A., Janota, C. P., & Frank, T. (1996). Frequency importance functions for words, sentences, and continuous discourse. Journal of Speech, Language, and Hearing Research, 39(4), 714-723.  
Raake, A., & Katz, B. F. (2006, May). US-based Method for Speech Reception Threshold Measurement in French. In LREC (pp. 2028-2033).  
Studebaker, G. A., Pavlovic, C. V., & Sherbecoe, R. L. (1987). A frequency importance function for continuous discourse. The Journal of the Acoustical Society of America, 81(4), 1130-1138.  

## Feedback on the project 

Although I had some basic programming experience in other languages, this was my first time programming in Python. It was also my first experience programming for digital signal processing (filtering, calculating SNRs, running FFTs...), and this is undeniably the part that took me the most time to research, understand and apply but it was also the most rewarding - it is why I chose to do this project in the first place. It was also my first time programming an experiment of this sort, and although it is hard to find ressources online for expyriment (except the xpy documentation, which is useful), it seems to be a useful tool that I will be using in the future. However, I have encountered many difficulties with it using MacOS. I had hoped to have more time to implement the data analysis and plotting aspects of the study, in preparation of data collection, but it was necessary to spend so much time on the speech stimulus generation and processing for these are definitely skills that will be useful to me in the future. 
In this class, I have gotten a first practical experience on the use of Python, on how to search and approach documentation. It has also opened up the many possibilities of what one can do with Python. As for this class, I would've expected more teaching regarding the different libraries of python (numpy, pandas, scipy,...), especially on how to use them efficiently. Since a lot is left for personal exploration (which is also a necessary step in learning how to program), it is very easy to miss on important aspects, useful functions or certain subtleties that may have a great yet unbeknownst impact on a research project. Additionally, it would be useful to learn how to solve common technical issues, such as how to deal with the different errors or crashes that can take place. 

