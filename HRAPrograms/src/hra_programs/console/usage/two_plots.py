'''
Created on Nov 26, 2013

@author: jurek
'''

import matplotlib.pyplot as plt
import numpy as np

#x = np.arange(10)


C2w, C2s, SD2w, SD2s = np.loadtxt('/home/jurek/volumes/doctoral/doktorat_przewod/dane/SVR_sliding__0001.res_out',  # @IgnorePep8
                       skiprows=1, delimiter=';', unpack=True) # @IgnorePep8
plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])
#plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])

#plt.plot(x, x)
#plt.plot(x, 2 * x)
#plt.plot(x, 3 * x)
#plt.plot(x, 4 * x)

#plt.legend(['y = x', 'y = 2x', 'y = 3x', 'y = 4x'], loc='upper left')


#plt.plot(SD2w)
#plt.plot(SD2s)

plt.plot(C2w)
plt.plot(C2s)

#plt.legend(['SD2w', 'SD2s'], loc='upper left')
plt.legend(['C2w', 'C2s'], loc='upper left')
plt.axes().set_xlabel('Time')

#plt.show()  # show plot
plt.savefig("/home/tmp/my_fig.png") # save plot
