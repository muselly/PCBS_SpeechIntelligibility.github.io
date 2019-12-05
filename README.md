# PCBS Project
## Speech Intelligibility Frequency Importance Function 

### Main Goal
The main goal of this project is to program a task to determine the relative importance of higher (above 2kHz) versus lower (below 2kHz) frequencies on speech intelligibility. Creating the stimuli involves speech signal processing resulting is varying signal-to-noise ratios (SNR) using speech shaped noise (SSN) on semantically unpredictable sentences (SUS). The program will collect participant string input (what they hear) and score their response by ccomparing it to a lexicon of French words. Finally, it'll determine the relative importance of higher versus lower frequencies for speech recognition for each participant. The entire project will be done in Python and the final output will be published on a GitHub webpage.

### Sound Materials
The speech material includes 288 semantically unpredictable sentences (SUS) of pre-defined structure and content (Raake & Katz, 2006). 
These sentences have been previously recorded and cleaned by Manuel Pariente. 
In this project, I will first be generating speech shaped noise based on these sentences which will be added to the sentence recordings at random phases in order to create 5 SNR conditions: 0, -3, -6, -9, -12 dB SNR. In order to determine the importance of each frequency band, there will be two frequency conditions: high frequency SNR (hiSNR) and low frequency SNR (loSNR). This will therefore involve lowpass and highpass filtering (de Cheveigné & Nelken, 2019).
Each sentence will be randomly assigned to a SNR and frequency condition. 

### Task
Each sentence will be played once to the subject. The subject will then be asked to type what they heard before moving on to the next sentence.
There will be 8 practice sentences in order to learn the task, and 280 test sentences (28 for each frequency and SNR condition). The subject will not be given any feedback. 

### Data Analysis
**Sentence scoring**: each correct keyword will be assigned one point. Each sentence contains four to five keywords, so total scores will be divided by the number of keywords in order to be normalized. To count the correct keywords, the subject input will be compared with the correct keywords (and their homophones). A keyword will be counted as right only if it is correclty chronologically placed relatively to the other keywords. Articles and punctuation will be ignored. 
For each subject, speech intelligibility (scores) will be plotted in terms of SNR for each frequency condition, and the SNR value for 50% speech intelligibility will be extracted and compared between frequency conditions. I expect that lower frequencies will be more important to speech intelligibility than higher frquencies, but the final goal of this manipulation is to compare individual variability in terms of the relative importance given to each frequency band. 

### Additional Notes
This project is related to my internship work at the Laboratoire des Systèmes Perceptifs with Daniel Pressnitzer, however it may or may not be used in our final study. If this ends up being used, it will be of a slightly different form, since a similar original task has already been programmed in Matlab using a completely different toolbox. 

### References
de Cheveigné, A., & Nelken, I. (2019). Filters: when, why, and how (not) to use them. Neuron, 102(2), 280-293.  
DePaolis, R. A., Janota, C. P., & Frank, T. (1996). Frequency importance functions for words, sentences, and continuous discourse. Journal of Speech, Language, and Hearing Research, 39(4), 714-723.  
Raake, A., & Katz, B. F. (2006, May). US-based Method for Speech Reception Threshold Measurement in French. In LREC (pp. 2028-2033).  
Studebaker, G. A., Pavlovic, C. V., & Sherbecoe, R. L. (1987). A frequency importance function for continuous discourse. The Journal of the Acoustical Society of America, 81(4), 1130-1138.  



