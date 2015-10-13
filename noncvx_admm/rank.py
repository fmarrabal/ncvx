"""
Copyright 2013 Steven Diamond

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

from .noncvx_variable import NonCvxVariable
import numpy as np

# TODO nuclear norm as convex relaxation?

class Rank(NonCvxVariable):
    """ A variable satisfying Rank(X) <= k. """
    def __init__(self, rows, cols, k, M=None, *args, **kwargs):
        self.k = k
        self.M = M
        super(Rank, self).__init__(rows, cols, *args, **kwargs)

    def init_z(self, random):
        """Initializes the value of the replicant variable.
        """
        if random:
            self.z.value = np.random.uniform(0, self.sigma, size=self.size)
        else:
            self.z.value = np.zeros(self.size)

    def _project(self, matrix):
        """All singular values except k-largest (by magnitude) set to zero.
        """
        U, s, V = np.linalg.svd(matrix)
        s[self.k+1:] = 0
        return U.dot(np.diag(s)).dot(V)

    # Constrain all entries to be the value in the matrix.
    def _fix(self, matrix):
        return [self == matrix]

    # def canonicalize(self):
    #     norm(self, 2) <= self.M