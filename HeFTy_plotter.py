# -*- coding: utf-8 -*-
'''
This code takes the .txt output from HeFTy (saved by right-clicking on the Time-Temperature history
and chosing "Export --> Save as Text...") and replots the data using a weighted mean of the goodness
of fit modeled by HeFTy.

It is meant to be run with only minimal user input: all you need to do is put your file name and
directory at the very top (lines 31 and 32). Then, to save the plot, uncomment (delete the intial #)
line XX and put the full file path that you would like to save to. This line is fairly intelligent.
If you put .jpg, .png, .pdf, etc. it will automatically know what format to save. I have it set up to
save as a 500 dpi .png right now, which is generaly good enough for publication quality of
graphical figures.

I've also added commenting throughout so you can understand what is being done. This will also
hopefully facilitate modifying the code however you see fit to best plot what you want to show.

Contact: Peter E. Martin <peter.martin-2@colorado.edu>
'''

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import combine_pvalues
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import random
plt.rcParams.update({'font.size': 12})



# =============================================================================
# Add your file name and directory here
# =============================================================================
root = Tk()
file = askopenfilename(title = 'Choose file to plot', filetypes = (("Tab-delimited Text file","*.txt"),))
root.wm_withdraw()

# user-defined variables for plotting
good_vs_acceptable = True
emphasize = 40
save = False
minimum = 0.05
maximum = 0.5
width = 6
height = 5

# Get the name of the file to save if requested
if save:
    save_out = asksaveasfilename(title = 'Save file',
                             defaultextension=".*",
                             filetypes = (("PNG",".png"),
                                          ("TIFF",".tiff"),
                                          ("PDF",".pdf"),
                                          ("JPEG",".jpg")))

# Start by getting meta-info from the header. This can accomodate up to 40 constraint boxes.
header = pd.read_csv(file,
                     sep = '\t',
                     names = list(range(20)),
                     nrows = 60)
firstcol = header[0].tolist() # Save the row labels to ID the various metadata
num_constraints = firstcol.index('Inversion completed')-2 # Count the number of constraints
head_length = firstcol.index('Fit')+1 # Find the overall length of the header

data_row = header.loc[firstcol.index('Individual paths')+1, :].values.tolist() #find the beginning of the data
# Find how many data inputs there were based on the number of GOF column labels
num_data = 0
for d in data_row:
    if type(d) == str:
        num_data+=1

# Use header info to get the constraints
constraints = np.genfromtxt(file,
                            delimiter = '\t',
                            skip_header = 2,
                            max_rows = num_constraints,
                            usecols = (1,2,3,4))

# Load the raw data
paths_raw = np.genfromtxt(file,
                          delimiter = '\t',
                          skip_header = head_length)

# Split the raw data into individual paths as a list of lists
# Each path is saved as [GOFs, Times, Temperatures]
# removes "best fit path" because this is always conained
# in the paths and should not recieve special treatment
# within the context of this data presentation
paths = []
dates = []
for r in range(2,len(paths_raw),2):
    paths.append([paths_raw[r+1][1:1+num_data],
                  paths_raw[r][2+num_data:],
                  paths_raw[r+1][2+num_data:]])
    dates.append(paths_raw[r][1:1+num_data])

# Use Fisher's method to combine p values into single p value
# Simply replace the list of GOFs with the combined GOF
for i in range(len(paths)):
    paths[i][0] = combine_pvalues(paths[i][0][~np.isnan(paths[i][0])],
                                  method='fisher')[1]

GOFs = [paths[i][0] for i in range(len(paths))] #create a new variable called GOFs using the numbers just generated
# The next five lines put the GOFs in order so that they can be plotted with the best-fit paths on top
indices = list(range(len(GOFs))) # Create a list of indices for each path
indices.sort(key=lambda x: GOFs[x]) # Match the indices to the GOFs
zorders = [0] * len(indices) # create an empty list to fill with each index
for i, x in enumerate(indices):
    zorders[x] = i # put the indices in order so that the highest GOF is plotted at the top

# Normalize the GOFs from 0-1 so they match the color map
normed_GOFs = [] # Create an empty list
for GOF in GOFs:
    normed_GOFs.append((GOF-minimum)/(maximum-minimum)) # Normalize each and add to the empty list

# Create a color map to color the paths based on GOF
cmap = matplotlib.cm.get_cmap('viridis') # Create colormap; others exist. See https://matplotlib.org/tutorials/colors/colormaps.html for others you can use.
colors = [] # Create an empty list for the color to plot
for g in normed_GOFs:
    colors.append(cmap(g)) # Get the color based on the colormap and weighted normalized GOF value

# make figure for plotting
size = (width, height)
fig, ax = plt.subplots(figsize=size)

if good_vs_acceptable:
    good_idx = np.where(np.array(GOFs)>maximum)[0]
    best_idx = GOFs.index(max(GOFs))
    good_idx = list(np.delete(good_idx, best_idx))

try:
    emph_idx = random.sample(good_idx, emphasize)
except ValueError:
    emph_idx = good_idx

# Plot each path
legend = False
for p in range(0,len(paths)):
    if GOFs[p]>maximum and good_vs_acceptable:
        if GOFs[p] == max(GOFs):
            legend = True
            # add a dummy line to plot the legend
            ax.plot([-10,-20], [-10,-20], # plot time and temperature
                      c = 'tab:orange', # use the color determined from the Goodness of Fit #tried firebrick, darkorange, tab:orange
                      lw = 1.0, # plot a slightly narrower line width so that all are visible
                      zorder = zorders[p],
                      label=f'Good Fits\n(GoF >{maximum})') # Put the better-fit paths on top
            if len(emph_idx)>0:
                ax.plot([-10,-20], [-10,-20], # plot time and temperature
                          c = '0.35', # use the color determined from the Goodness of Fit #tried firebrick, darkorange, tab:orange
                          lw = 1.0, # plot a slightly narrower line width so that all are visible
                          zorder = zorders[p],
                          label='Randomly-chosen\ngood fits\n(for improved visibility)') # Put the better-fit paths on top
            ax.plot(paths[p][1], paths[p][2], # plot time and temperature
                      c = 'k', # use the color determined from the Goodness of Fit #tried firebrick, darkorange, tab:orange
                      lw = 2, # plot a slightly narrower line width so that all are visible
                      zorder = zorders[p]*100,
                      label='Best-fit path') # Put the better-fit paths on top
        elif p in emph_idx:
            ax.plot(paths[p][1], paths[p][2], # plot time and temperature
                  c = '0.35', # use the color determined from the Goodness of Fit #tried firebrick, darkorange, tab:orange
                  lw = 0.5, # plot a slightly narrower line width so that all are visible
                  zorder = zorders[p]*100) # emphasize these paths by putting on top
        else:
            ax.plot(paths[p][1], paths[p][2], # plot time and temperature
                  c = 'tab:orange', # use the color determined from the Goodness of Fit #tried firebrick, darkorange, tab:orange
                  lw = 0.5, # plot a slightly narrower line width so that all are visible
                  zorder = zorders[p]) # Always put the randomly chosen lines on top
    else:
        ax.plot(paths[p][1], paths[p][2], # plot time and temperature
                  c = colors[p], # use the color determined from the Goodness of Fit
                  lw = 0.3, # plot a slightly narrower line width so that all are visible
                  zorder = zorders[p]) # Put the better-fit paths on top

# This code block plots the constraint boxes and finds the maximum time and temperate to adjust the axes
max_T = 0 # create empty variables for maximum time and temperature to update as constraint boxes are plotted
max_t = 0
for c in constraints:
    ax.add_patch(patches.Rectangle((c[1], c[3]),(c[0]-c[1]),(c[2]-c[3]), # plot each constraint as a box
                      ec = 'k', # make the boxes black
                      lw = 1, # set the line thickness
                      fill = False, # prevent the box from being filled
                      zorder = len(paths)*100)) # Always plot the boxes on top of the paths
    # The next four lines update the max t and T to set the axes to plot on
    if c[0]>max_t:
        max_t = c[0]*1.05
    if c[2]>max_T:
        max_T = c[2]*1.05

ticks = list(np.linspace(minimum, maximum, 6)) # set the non-normalized values as labels on the colorbar
normalize = matplotlib.colors.Normalize(vmin=minimum, vmax=maximum) # normalize the colorbar
cbar = plt.colorbar(matplotlib.cm.ScalarMappable(norm=normalize, cmap=cmap), # Plot the colorbar
                    orientation='vertical', # put colorbar to the right
                    fraction=.1, # set the width of the colorbar
                    ticks = ticks) # relabel the colorbar with the GOF values
cbar.set_label('Goodness of Fit (weighted mean)') # Give the colorbar a title
ticks = [round(t, 2) for t in ticks]
if not good_vs_acceptable:
    ticks[-1] = '≥'+ str(ticks[-1])
cbar.set_ticklabels(ticks) # round the tick labels so they are at most 2 digits

ax.grid(which='major',axis='both', ls = '--') # add a grid to easily trace t-T
# plt.title('ADD TITLE HERE') # if you would like a title, delete the first # and add the title
# ax.set_xlim(max_t, 0) # set the x axis limits
ax.set_xlim(100, 0)
ax.set_ylim(max_T, 0) # set the y axis limits
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
ax.set_xlabel('Age (Ma)') # label the x axis
ax.set_ylabel('Temperature ($\mathregular{^o}$C)') # label the y axis

if good_vs_acceptable and legend:
    plt.legend()
plt.tight_layout()
if save:
    plt.savefig(save_out, dpi = 800) # this line lets you save the plot if you want
plt.show() # show the plot