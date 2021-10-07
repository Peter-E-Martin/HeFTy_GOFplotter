# HeFTy GOF Plotter
## Intro
This is a brief code that allows HeFTy results to be plotted in a slightly more complex way than the thresholded values provided by default. Instead of magenta being coded to "good" Goodness of Fit (GOF) values and green to "acceptable", it plots a weighted average of the "acceptable" paths according to their actual values using a color ramp, and shows an envelope for the "good" paths. This approach allows the user to determine which acceptable paths are better supported by the data.

The code reads in the raw Tab-delimited Text File (.txt) produced by HeFTy when right-clicking on the inverse modeling Time-Temperature History results and choosing Export→Save as Text. The output is by default the matplotlib user interface window, though the image can be resized, labels changed, and figure saved at high dpi with simple changes in the code, which are noted by the commenting.

The test.txt is a test file to make sure that the plotter is working for you. It was produced using a quick HeFTy inverse model of an apatite helium datum with uncorrected age of 10 ± 1 Ma. The output from this should look like the test_result.png image in the repository.

## Statistical Background
The weighted mean GOF is calculated using weights of 1-GOF for each GOF parameter.In other words, each GOF metric is weighted by how poorly it fits the data. This should give an overall conservative view of how well each path fits the data.

Only the "acceptable" paths are plotted using this method. The "good" paths, with a GOF metric of >0.5, are instead shown using the envelope of good paths. The rationale behind this threshold is that, given the probability distribution described by the uncertainties given to HeFTy, any path with a GOF value of >0.5 is at the limit of staistical inference with regards to your data. In the context of HeFTy, where time-temperature paths are being tested against a dataset with specific uncertainties, the "good" paths are those where, given a resampling of your data using their uncertainties, there is a 50% chance that the path would provide a worse fit. In this way, the 0.5 GOF level is the limit of statistcal inference for HeFTy given the uncertainties inherent in the data. We therefore do not distinguish the "good" fit paths.
