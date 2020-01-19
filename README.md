# PCBS Project
## Speech Intelligibility Frequency Importance Function 

### Main Goal
The main goal of this project is to program a task to determine the relative importance of higher (above 2kHz) versus lower (below 2kHz) frequencies on speech intelligibility. Creating the stimuli involves speech signal processing resulting is varying signal-to-noise ratios (SNR) using braodband speech shaped noise (SSN) on narrowband digit triplets in French. The program will collect participant input digits (what they hear) and score their response. Finally, it'll determine the relative importance of higher versus lower frequencies for speech recognition for each participant. The entire project will be done in Python and the final output will be published on a GitHub webpage.

### Sound Materials
The speech material includes recordings of the nine digits in French, each one second long. On each trial, a triplet of digits in noise will be presented. 
I will be recording and cleaning these digit recordings.  
In this project, I will first be generating speech shaped noise based on these sentences which will be added to the sentence recordings at random phases in order to create 5 SNR conditions: 0, -3, -6, -9, -12 dB SNR (calculated using RMS amplitude of signal). In order to determine the importance of each frequency band, there will be two frequency conditions: high frequency SNR (hi) and low frequency SNR (lo). This will therefore involve lowpass and highpass filtering (de Cheveigné & Nelken, 2019).
Each sentence will be randomly assigned to a SNR and frequency condition. 

### Task
Each digit triplet will be played once to the subject. The subject will then be asked to type what they heard before moving on to the next triplet.
There will be 9 practice trials in order to learn the task, and 300 test sentences (30 for each frequency and SNR condition). If the participant doesn't know what digit was presented, they must input a '0' instead. The subject will not be given any feedback. 

### Data Analysis
**Sentence scoring**: each correct digit will be assigned one point. '0' responses will not be assigned any points. 
For each subject, speech intelligibility (scores) will be plotted in terms of SNR for each frequency condition, and the SNR value for 50% speech intelligibility will be extracted and compared between frequency conditions. I expect that higher frequencies will be more important to speech intelligibility than lower frquencies, but the final goal of this manipulation is to compare individual variability in terms of the relative importance given to each frequency band. 

### Additional Notes
This project is related to my internship work at the Laboratoire des Systèmes Perceptifs with Daniel Pressnitzer, however it may or may not be used in our final study. If this ends up being used, it will be of a slightly different form, since a similar original task has already been programmed in Matlab using a completely different toolbox. 

### References
de Cheveigné, A., & Nelken, I. (2019). Filters: when, why, and how (not) to use them. Neuron, 102(2), 280-293.  
DePaolis, R. A., Janota, C. P., & Frank, T. (1996). Frequency importance functions for words, sentences, and continuous discourse. Journal of Speech, Language, and Hearing Research, 39(4), 714-723.  
Raake, A., & Katz, B. F. (2006, May). US-based Method for Speech Reception Threshold Measurement in French. In LREC (pp. 2028-2033).  
Studebaker, G. A., Pavlovic, C. V., & Sherbecoe, R. L. (1987). A frequency importance function for continuous discourse. The Journal of the Acoustical Society of America, 81(4), 1130-1138.  



