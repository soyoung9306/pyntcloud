import numpy as np

from .base import ScalarField
from ..utils.array import cov3D


class KNeighborsScalarField(ScalarField):
    """
    Parameters
    ----------
    k_neighbors: ndarray
        (N, k, 3) The k neighbours associated to each of the N points.
    """

    def __init__(self, *, pyntcloud, k_neighbors):
        super().__init__(pyntcloud=pyntcloud)
        self.k_neighbors_idx = k_neighbors

    def extract_info(self):
        self.k_neighbors = self.pyntcloud.xyz[self.k_neighbors_idx]


class EigenValues(KNeighborsScalarField):
    """Compute the eigen values of each point's neighbourhood.
    """
    def compute(self):
        cov = cov3D(self.k_neighbors)
        eigenvalues = np.linalg.eigvals(cov)
        sort = eigenvalues.argsort()

        # range from 0-shape[0] to allow indexing along axis 1 and 2
        idx_trick = range(eigenvalues.shape[0])

        e1 = eigenvalues[idx_trick, sort[:, 2]]
        e2 = eigenvalues[idx_trick, sort[:, 1]]
        e3 = eigenvalues[idx_trick, sort[:, 0]]

        k = self.k_neighbors.shape[1]
        self.to_be_added["e1({})".format(k)] = e1
        self.to_be_added["e2({})".format(k)] = e2
        self.to_be_added["e3({})".format(k)] = e3


class EigenDecomposition(KNeighborsScalarField):
    """Compute the eigen decomposition of each point's neighbourhood.
    """
    def compute(self):
        cov = cov3D(self.k_neighbors)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        sort = eigenvalues.argsort()

        # range from 0-shape[0] to allow indexing along axis 1 and 2
        idx_trick = range(eigenvalues.shape[0])

        e1 = eigenvalues[idx_trick, sort[:, 2]]
        e2 = eigenvalues[idx_trick, sort[:, 1]]
        e3 = eigenvalues[idx_trick, sort[:, 0]]

        k = self.k_neighbors.shape[1]
        self.to_be_added["e1({})".format(k)] = e1
        self.to_be_added["e2({})".format(k)] = e2
        self.to_be_added["e3({})".format(k)] = e3

        ev1 = eigenvectors[idx_trick, :, sort[:, 2]]
        ev2 = eigenvectors[idx_trick, :, sort[:, 1]]
        ev3 = eigenvectors[idx_trick, :, sort[:, 0]]

        self.to_be_added["ev1({})".format(k)] = ev1.tolist()
        self.to_be_added["ev2({})".format(k)] = ev2.tolist()
        self.to_be_added["ev3({})".format(k)] = ev3.tolist()


class UnorientedNormals(KNeighborsScalarField):
    """Compute normals using SVD.
    """
    def compute(self):
        cov = cov3D(self.k_neighbors)
        u, s, v = np.linalg.svd(cov)

        normals = u[:, :, -1]

        k = self.k_neighbors.shape[1]
        self.to_be_added["nx({})".format(k)] = normals[:, 0]
        self.to_be_added["ny({})".format(k)] = normals[:, 1]
        self.to_be_added["nz({})".format(k)] = normals[:, 2]
