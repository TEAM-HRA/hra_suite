'''
Created on Apr 1, 2014

@author: jurek
'''
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.image as mpimg

f = plt.figure()
#plt.tight_layout()

#gs = gridspec.GridSpec(1, 2, width_ratios=[2,1])
gs = gridspec.GridSpec(5, 1, height_ratios=[6,24,24,23,23])
gs.update(left=0.03, right=0.98, hspace=0.15, wspace=0.4)

ax1 = plt.subplot(gs[0])
#ax1.set_axis_off()
ax1.get_xaxis().set_visible(False)
ax1.get_yaxis().set_visible(False)
ax1.autoscale_view('tight')
pyp = mpimg.imread('/home/jurek/tmp/szeroki_tytul.png')
ax1.imshow(pyp) #, origin='lower')
ax1.set_frame_on(False)

#ax1.patch.set_linewidth(10.0)
ax2 = plt.subplot(gs[1])

ax2 = plt.subplot(gs[2])
ax2 = plt.subplot(gs[3])
ax2 = plt.subplot(gs[4])

#gs.tight_layout(f, pad=0, w_pad=0, h_pad=0.1)
#gs.tight_layout(f, pad=0.01, w_pad=0.01, h_pad=0.01)

#gs.tight_layout(f, pad=0.2, w_pad=6, h_pad=0.1)
plt.show()
