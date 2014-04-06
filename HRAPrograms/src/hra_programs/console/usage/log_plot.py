'''
Created on Nov 26, 2013

@author: jurek
'''

import matplotlib.pyplot as plt
import numpy as np
from numpy.core.function_base import linspace


x = linspace(10, 100, 90)
plt.plot(x, np.log(x))
plt.show()
