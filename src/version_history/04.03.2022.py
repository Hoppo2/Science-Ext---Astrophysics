from astroquery.mast import Observations, Catalogs, Tesscut, Zcut
from astropy.coordinates import SkyCoord

import tensorflow as tf
import sklearn as skl
from sklearn import linear_model
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from yellowbrick.cluster import SilhouetteVisualizer

import csv
import os


class _Data:
    def __init__(self):
        self.data = pd.read_csv("data_sets/COMBO17.csv")
        self.points = np.array(
            list(zip(self.data["Mcz"], self.data["W420FE"], self.data["W462FE"], self.data["W485FD"],
                     self.data["W518FE"],
                     self.data["W571FS"], self.data["W604FE"],
                     self.data["W646FD"], self.data["W696FE"], self.data["W753FE"], self.data["W815FS"],
                     self.data["W856FD"], self.data["W914FD"],
                     self.data["W914FE"]))
        )
        self.restricted = np.array(
            list(zip(self.data["Mcz"], self.data["ApDRmag"])) # TODO: Change ApDRmag to luminosity magnitude
        )


class Cluster(_Data):
    def __init__(self):
        _Data.__init__(self)

    def model(self, n):
        model = KMeans(n_clusters=n)
        model.fit(self.restricted)

        return model

    def visualiser(self, model):
        visualiser = SilhouetteVisualizer(model, colors='yellowbrick')
        visualiser.fit(self.restricted)

        visualiser.show()

    def two(self):
        xdata=self.data["Mcz"]
        ydata=self.data["W462FE"]

        fig = plt.figure(figsize=(4, 4))

        ax = fig.add_subplot(111)

        ax.scatter(xdata, ydata)
        ax.set_xlabel('Mcz')
        ax.set_ylabel("W462FE")

        plt.show()

    def boss(self):
        xdata = self.data["W462FE"]
        ydata = self.data["Mcz"]
        zdata = self.data["W914FD"]

        fig = plt.figure(figsize=(4, 4))

        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(xdata, ydata, zdata)
        ax.set_xlabel('W462FE')
        ax.set_ylabel("Mcz")
        ax.set_zlabel('W914FD')

        plt.show()

    def three_band(self):
        xdata = self.data["W462FE"]
        ydata = self.data["W646FD"]
        zdata = self.data["W914FD"]
        cdata = self.data["Mcz"]

        fig = plt.figure(figsize=(4, 4))

        ax = fig.add_subplot(111, projection='3d')

        img = ax.scatter(xdata, ydata, zdata, c=cdata, cmap=plt.hot())
        fig.colorbar(img)
        ax.set_xlabel('W462FE')
        ax.set_ylabel('W646FD')
        ax.set_zlabel('W914FD')

        plt.show()


if __name__ == "__main__":
    Cluster().two()
    # Cluster().visualiser(_model)
    # Cluster().three_band()
