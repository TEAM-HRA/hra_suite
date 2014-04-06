'''
Created on Apr 1, 2014

@author: jurek
'''
# demo 3 : gridspec with subplotpars set.
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

f = plt.figure()

plt.suptitle("GirdSpec w/ different subplotpars")

gs1 = GridSpec(3, 3)
gs1.update(left=0.05, right=0.48, wspace=0.05)
ax1 = plt.subplot(gs1[:-1, :])
ax2 = plt.subplot(gs1[-1, :-1])
ax3 = plt.subplot(gs1[-1, -1])

gs2 = GridSpec(3, 3)
gs2.update(left=0.55, right=0.98, hspace=0.05)
ax4 = plt.subplot(gs2[:, :-1])
ax5 = plt.subplot(gs2[:-1, -1])
ax6 = plt.subplot(gs2[-1, -1])

#make_ticklabels_invisible(plt.gcf())

plt.show()
