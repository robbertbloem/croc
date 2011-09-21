from __future__ import print_function
from __future__ import division

import numpy

# speed of light
c_ms = 2.9979e8 # m/s
c_cms = 100 * c_ms # cm/s
c_cmfs = c_cms / 1e-15 # cm/fs

# conversions speed of light <-> wavenumbers
wavenumberToInvFs = c_cms * 1e-15
wavenumberToInvPs = c_cms * 1e-12
wavenumberToInvSec = c_cms

# fringes
hene_fringe_fs = 1e15 * 632e-9 / c_ms