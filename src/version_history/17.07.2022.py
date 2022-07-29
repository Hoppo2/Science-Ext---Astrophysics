# TODO:
#  Analyse galaxy density in the clusters
#  Analyse other possible environmental impacts
#   a

from datetime import datetime

import requests

import xlsxwriter
import pickle
import json

from os.path import exists

import pandas as pd
import scipy.stats as scipy
import impyute as impy
import numpy as np
import matplotlib.pyplot as plt
from conversions import *
from astropy.io import fits

from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, silhouette_score
from sklearn.cluster import KMeans, OPTICS
from yellowbrick.cluster import SilhouetteVisualizer
from matplotlib import gridspec

from dataclasses import dataclass


class pkl(object):
    @staticmethod
    def save_model(model, name):
        with open(f'{name}_{datetime.now().date()}', 'wb') as handle:
            pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def read_model(name):
        with open(f'{name}', 'rb') as handle:
            model = pickle.load(handle)
        return model


class metrics(object):
    def __init__(self, model, class_instance=None):
        self.model = model
        self.cls_instance = class_instance

    def silhouette(self, generate_graph: bool = True, data=None):
        """
        This method creates a visualiser plot based upon a cluster model.
        :return: visualiser object
        """
        if type(self.model) != KMeans:
            raise TypeError(
                f"Wasn't able to evaluate silhouette metric from the model type: {type(self.model)}. "
                f"Requires KMeans model instead."
            )

        if self.cls_instance is not None:
            x_data = self.cls_instance.__getattribute__("X_train")
        else:
            x_data = data

        score = silhouette_score(X=x_data, labels=self.model.labels_)

        if generate_graph:
            visualiser = SilhouetteVisualizer(self.model, colors='yellowbrick')
            visualiser.fit(X=x_data)  # x_data is the data array used in the creation of cluster model
            visualiser.fit(X=x_data)  # x_data is the combo_data array used in the creation of cluster model
            visualiser.show()
            return [visualiser, score]
        else:
            return score

    def reachability(self):
        if type(self.model) != OPTICS:
            raise TypeError(
                f"Wasn't able to evaluate reachability metric from the model type: {type(self.model)}. "
                f"Requires OPTICS model instead. "
            )
        x_data = self.cls_instance.__getattribute__("X_train")

        space = np.arange(len(x_data))
        reachability = self.model.reachability_[self.model.ordering_]
        labels = self.model.labels_[self.model.ordering_]

        plt.figure(figsize=(10, 7))
        G = gridspec.GridSpec(2, 3)
        ax1 = plt.subplot(G[0, :])

        colors = ["g.", "r.", "b.", "y.", "c."]
        for klass, color in zip(range(0, 5), colors):
            Xk = space[labels == klass]
            Rk = reachability[labels == klass]
            ax1.plot(Xk, Rk, color, alpha=0.3)
        ax1.plot(space[labels == -1], reachability[labels == -1], "k.", alpha=0.3)
        ax1.plot(space, np.full_like(space, 2.0, dtype=float), "k-", alpha=0.5)
        ax1.plot(space, np.full_like(space, 0.5, dtype=float), "k-.", alpha=0.5)
        ax1.set_ylabel("Reachability (epsilon distance)")
        ax1.set_title("Reachability Plot")

        plt.show()

    @staticmethod
    def inertia_graph(n_iterations: int):
        """
        This graphs the inertia score of the range of clusters between 2 and n_iterations.
        :param n_iterations: Number of iterations (k) calculated. The inertia of the model calculated by the
        number of clusters range (2, n_iterations) will be graphed.
        :return: plt object
        """
        _inertia_score = []
        k = range(2, n_iterations)
        for n in k:  # TODO: Make sure this works
            _inertia_score.append(Cluster().kmeans(n=n, save=False).inertia_)

        plt.plot(k, _inertia_score)
        plt.xlabel("n clusters")
        plt.ylabel("inertia")
        plt.show()

    def silhouette_graph(self, n_iterations: int):
        if type(self.model) != KMeans:
            raise TypeError(
                f"Wasn't able to evaluate inertia metric from the model type: {type(self.model)}. "
                f"Requires KMeans model instead."
            )
        _silhouette_score = []
        k = range(2, n_iterations)
        for n in k:  # TODO: Make sure this works
            cluster = Cluster()
            model = cluster.kmeans(n=n, save=False)
            _silhouette_score.append(metrics(class_instance=cluster, model=model).silhouette(generate_graph=False)[1])

        plt.plot(k, _silhouette_score)
        plt.xlabel("n clusters")
        plt.ylabel("inertia")
        plt.show()


@dataclass
class _Data(object):
class _COMBO_Data(object):
    """
    This class (_Data) constructs the arrays for various compilations of data
    This class (_Data) constructs the arrays for various compilations of combo_data
    The flux_to_luminosity class in conversions.py controls the conversion from flux to luminosity.
    Currently there is no conversion from flux to luminosity. I.e. flux_to_luminosity returns original flux parameter.
    """
    if exists("combo_data"):
        """
        IF THE CLEANSED DATA HAS BEEN SAVED TO A FILE, IT WILL BE LOADED INSTEAD OF CLEANSING IT AGAIN
        """
        with open(f'combo_data', 'rb') as handle:
            save_data_output = pickle.load(handle)

        columns: np.ndarray = save_data_output[0]["columns"]
        Mcz: np.ndarray = save_data_output[0]["Mcz"]
        Incl_Mcz_Johnson: np.ndarray = save_data_output[0]["Incl_Mcz_Johnson"]
        Excl_Mcz_Johnson: np.ndarray = save_data_output[0]["Excl_Mcz_Johnson"]
        Incl_Mcz_Sloan: np.ndarray = save_data_output[0]["Incl_Mcz_Sloan"]
        Excl_Mcz_Sloan: np.ndarray = save_data_output[0]["Excl_Mcz_Sloan"]
        Mcz_prop: np.ndarray = save_data_output[0]["Mcz_prop"]
        percent_nan = save_data_output[1]

    with fits.open('data_sets/combo17.fits') as hdul:
        # hdul.verify('fix')
        data = hdul[1].data
        cols = hdul[1].columns
        print(percent_nan)

    else:
        with fits.open('data_sets/combo17.fits') as hdul:
            hdul.verify('fix')
            i_data = hdul[1].data
            cols = hdul[1].columns

    columns: fits.column.ColDefs = cols
        columns: fits.column.ColDefs = cols

    """
    LUMINOSITIES
    """
        """
        CREATING A DATA MASK FOR PHOT_FLAG >= 8 AND STELLARITY < 0.25. 
        THIS FILTERS THE DATA TO REMOVE PROBLEMATIC DATAPOINTS AND ONLY INCLUDE STARS.
        """

        phot_mask = (i_data["phot_flag"] < 8)  # A mask created of the data to exclude erroneous data-points.
        galaxy_mask = (i_data["stellarity"] < 0.25)  # A mask created includeing all galaxies.

        total_mask = np.logical_and(phot_mask, galaxy_mask)  # Combining both phot and galaxy mask with an and statement

        data = i_data[total_mask]  # Application of the phot_flag mask to initial combo_data array.

        percent_nan = {  # Calculation for the percentage of missing combo_data in each of the used arrays.
            "MC_z": np.count_nonzero(np.isnan(data["MC_z"])) / data["MC_z"].size,

            "UjMAG": np.count_nonzero(np.isnan(data["UjMAG"])) / data["UjMAG"].size,
            "BjMAG": np.count_nonzero(np.isnan(data["BjMAG"])) / data["BjMAG"].size,
            "VjMAG": np.count_nonzero(np.isnan(data["VjMAG"])) / data["VjMAG"].size,

            "usMAG": np.count_nonzero(np.isnan(data["usMAG"])) / data["usMAG"].size,
            "gsMAG": np.count_nonzero(np.isnan(data["gsMAG"])) / data["gsMAG"].size,
            "rsMAG": np.count_nonzero(np.isnan(data["rsMAG"])) / data["rsMAG"].size,

            "x": np.count_nonzero(np.isnan(data["x"])) / data["x"].size,
            "y": np.count_nonzero(np.isnan(data["y"])) / data["y"].size,

            "MinAxis": np.count_nonzero(np.isnan(data["MinAxis"])) / data["MinAxis"].size,
            "MajAxis": np.count_nonzero(np.isnan(data["MajAxis"])) / data["MajAxis"].size,

            "dl": np.count_nonzero(np.isnan(data["dl"])) / data["dl"].size,
            "ApD_Rmag": np.count_nonzero(np.isnan(data["ApD_Rmag"])) / data["ApD_Rmag"].size,
            "mu_max": np.count_nonzero(np.isnan(data["mu_max"])) / data["mu_max"].size,
            "Rmag": np.count_nonzero(np.isnan(data["Rmag"])) / data["Rmag"].size,
        }

        """
        FORMATION OF DAUGHTER ARRAYS USED IN THE REGRESSION, CLUSTER AND DENSITY ANALYSIS
        """

    Incl_Mcz_Johnson: np.ndarray = np.array(
        list(zip(
            data["MC_z"], data["UjMAG"], data["BjMAG"], data["VjMAG"],
        uncertainty = {
            "e_UjMag": data["e_UjMag"].mean(),
            "e_BjMag": data["e_BjMag"].mean(),
            "e_VjMag": data["e_VjMag"].mean(),
            "e_usMag": data["e_usMag"].mean(),
            "e_gsMag": data["e_gsMag"].mean(),
            "e_rsMag": data["e_rsMag"].mean()
        }

        print(uncertainty)

        Incl_Mcz_Johnson: np.ndarray = impy.em(np.array(
            list(zip(
                data["MC_z"], data["UjMAG"], data["BjMAG"], data["VjMAG"]
            )), dtype=np.float64
        ))
    )

    Excl_Mcz_Johnson: np.ndarray = np.array(
        list(zip(
            data["UjMAG"], data["BjMAG"], data["VjMAG"]
        Excl_Mcz_Johnson: np.ndarray = impy.em(np.array(
            list(zip(
                data["UjMAG"], data["BjMAG"], data["VjMAG"]
            )), dtype=np.float64
        ))
    )

    Incl_Mcz_Sloan: np.ndarray = np.array(
        list(zip(
            data["MC_z"], data["usMAG"], data["gsMAG"], data["rsMAG"]
        Incl_Mcz_Sloan: np.ndarray = impy.em(np.array(
            list(zip(
                data["MC_z"], data["usMAG"], data["gsMAG"], data["rsMAG"]
            )), dtype=np.float64
        ))
    )

    Excl_Mcz_Sloan: np.ndarray = np.array(
        list(zip(
            data["usMAG"], data["gsMAG"], data["rsMAG"]
        ))
    )

    Incl_Mcz_Bessel: np.ndarray = np.array(
        list(zip(
            data["MC_z"], data["UbMAG"], data["BbMAG"], data["VbMAG"]
        Excl_Mcz_Sloan: np.ndarray = impy.em(np.array(
            list(zip(
                data["usMAG"], data["gsMAG"], data["rsMAG"]
            )), dtype=np.float64
        ))
    )

    Excl_Mcz_Bessel: np.ndarray = np.array(
        list(zip(
            data["UbMAG"], data["BbMAG"], data["VbMAG"]
        ))
    )

    """
    FLUX
    """

    """
    Incl_Mcz: np.ndarray = np.array(
        list(zip(
            data["MC_z"],
            data["W462FE"],
            data["W485FD"],
            data["W518FE"],
            data["W571FS"],
            data["W604FE"],
            data["W646FD"],
            data["W696FE"],
            data["W753FE"],
            data["W815FS"],
            data["W856FD"],
            data["W914FD"]
        Mcz_prop: np.ndarray = impy.em(np.array(
            list(zip(
                data["MC_z"],
                data["x"], data["y"],
                data["ApD_Rmag"],
                data["MajAxis"], data["MinAxis"],
                data["dl"],
                data["mu_max"],
                data["Rmag"]
            )), dtype=np.float64
        ))
    )

    Excl_Mcz: np.ndarray = np.array(
        list(zip(
            data["W462FE"],
            data["W485FD"],
            data["W518FE"],
            data["W571FS"],
            data["W604FE"],
            data["W646FD"],
            data["W696FE"],
            data["W753FE"],
            data["W815FS"],
            data["W856FD"],
            data["W914FD"]
        ))
    )
    """

    """
    EXTRA
    """

    Mcz: np.ndarray = np.array(
        list(zip(
            data["MC_z"]
        ))
    )
        Mcz: np.ndarray = np.array(
            Incl_Mcz_Johnson[0]
        )

    Mcz_prop: np.ndarray = np.array(
        list(zip(
            data["MC_z"], data["x"], data["y"], data["ApD_Rmag"]
        ))
    )
        """
        SAVING THE DATA TO A FILE SO THIS CLEANSING WILL NOT HAVE TO BE EVALUATED EACH TIME
        """

        save_data_input = [{
            "columns": columns,
            "Mcz": Mcz,
            "Incl_Mcz_Johnson": Incl_Mcz_Johnson,
            "Incl_Mcz_Sloan": Incl_Mcz_Sloan,
            "Excl_Mcz_Johnson": Excl_Mcz_Johnson,
            "Excl_Mcz_Sloan": Excl_Mcz_Sloan,
            "Mcz_prop": Mcz_prop
        }, percent_nan]

        with open(f'combo_data', 'wb') as handle:
            pickle.dump(save_data_input, handle, protocol=pickle.HIGHEST_PROTOCOL)


class Environment(_COMBO_Data):
    def __init__(self, *redshift_range):
        """

        :param redshift_range:
        """
        _COMBO_Data.__init__(self)

        self.a_min_z = redshift_range[0][0]
        self.a_max_z = redshift_range[0][1]
        self.b_min_z = None
        self.b_max_z = None

    def density_graph(self, bins: int = 0.002):
        """
        Two-dimensional graph of the relationship between galaxy luminosity (y axis) and redshift (x axis)
        :return: plt object
        """

        array = np.arange(0.1, 1.91, 0.01)
        values = [[], []]
        for i in array:
            _min, _max = i-bins, i+bins

            a_mcz_mask = np.logical_and((_min < self.Mcz_prop[:, 0]), (_max > self.Mcz_prop[:, 0]))
            a_Mcz_prop = self.Mcz_prop[a_mcz_mask]
            a_galaxies = [a_Mcz_prop[:, 1], a_Mcz_prop[:, 2]]

            if len(a_galaxies[0])==0:
                a_galaxies[0]=[0]
            if len(a_galaxies[1])==0:
                a_galaxies[1]=[0]

            a_x_range = min(a_galaxies[0]) - max(a_galaxies[0])
            a_y_range = min(a_galaxies[1]) - max(a_galaxies[1])

            values[0].append(i)
            if not a_galaxies[0][0]==0:
                values[1].append(len(a_galaxies[0]) / (a_x_range * a_y_range))
            else:
                values[1].append(0)

        redshift_mask = (self.Incl_Mcz_Johnson[:, 0] < 2)

        x_values1 = np.array(values[0])
        y_values1 = np.array(values[1])

        x_values2_r = self.Incl_Mcz_Johnson[:, 0][redshift_mask]
        y_values2_u = self.Incl_Mcz_Johnson[:, 1][redshift_mask]
        y_values2_v = self.Incl_Mcz_Johnson[:, 2][redshift_mask]
        y_values2_b = self.Incl_Mcz_Johnson[:, 3][redshift_mask]

        fig, ax1 = plt.subplots(figsize=(9, 6))

        ax2 = ax1.twinx()

        ax1_colour = "0.4"
        ax2_colour = "0"

        ax1.scatter(x_values2_r, y_values2_u+0, color=ax1_colour, s=0.1)
        ax1.scatter(x_values2_r, y_values2_b+10, color=ax1_colour, s=0.1)
        ax1.scatter(x_values2_r, y_values2_v+20, color=ax1_colour, s=0.1)
        ax2.plot(x_values1, y_values1, color=ax2_colour)

        ax1.set_xlabel("Redshift (z)")
        ax1.set_ylabel("Luminosity (mag)", color=ax1_colour)
        ax1.tick_params(axis="y", labelcolor=ax1_colour)

        ax2.set_ylabel("Density (n galaxies/pixel^2)", color=ax2_colour)
        ax2.tick_params(axis="y", labelcolor=ax2_colour)

        fig.suptitle("Overlay of Luminosity VS Redshift (Left) and Density VS Redshift (Right) in COMBO17 Survey", fontsize=12)
        ax1.grid(b=None)
        ax2.grid(b=None)
        plt.show()

    def density_histogram(self, bins: int = 50):
        """
        Generates a histogram fo the density of galaxies across the cfds_r.fit image
        :param bins: [1, 2] array
        :return: density of galaxies per pixel^2
        """

        """
        DENSITY
        """

        a_mcz_mask = np.logical_and((self.a_min_z < self.Mcz_prop[:, 0]), (self.a_max_z > self.Mcz_prop[:, 0]))
        a_Mcz_prop = self.Mcz_prop[a_mcz_mask]
        a_galaxies = [a_Mcz_prop[:, 1], a_Mcz_prop[:, 2]]

@dataclass
class _STAGES(object):
    pass
        a_x_range = min(a_galaxies[0]) - max(a_galaxies[0])
        a_y_range = min(a_galaxies[1]) - max(a_galaxies[1])

        a_density = len(a_galaxies[0]) / (a_x_range * a_y_range)

class Properties(_Data):
    def __init__(self, max_redshift, min_redshift):
        _Data.__init__(self)
        """
        HISTOGRAM
        """

        self.max_z = max_redshift
        self.min_z = min_redshift
        a_mcz_mask = np.logical_and((self.a_min_z < self.Mcz_prop[:, 0]), (self.a_max_z > self.Mcz_prop[:, 0]))
        a_Mcz_prop = self.Mcz_prop[a_mcz_mask]
        a_galaxies = [a_Mcz_prop[:, 1], a_Mcz_prop[:, 2]]

        plt.hist2d(a_galaxies[0], a_galaxies[1], bins=(bins, bins), cmap=plt.cm.Greys)
        plt.colorbar(label='n Galaxies')

        # Add labels
        plt.title(f'Density of galaxies in cdfs_r.fit image ({self.a_min_z}<z<{self.a_max_z})')
        plt.xlabel('x coordinate (pixels)')
        plt.ylabel('y coordinate (pixels)')

        plt.show()

        return a_density

    def density(self):
        pos_range = [[], []]
        for i in self.Mcz_prop:
            if self.min_z < i[0] < self.max_z:
                pos_range[0].append(i[1])
                pos_range[1].append(i[2])
        print(len(pos_range[0]), len(pos_range[1]))
        x_range = max(pos_range[0]) - min(pos_range[0])
        y_range = max(pos_range[1]) - min(pos_range[1])
        """
        Calculates the density of a galaxy in a determined redshift range
        :return:
        """

        a_mcz_mask = np.logical_and((self.a_min_z < self.Mcz_prop[:, 0]), (self.a_max_z > self.Mcz_prop[:, 0]))
        a_Mcz_prop = self.Mcz_prop[a_mcz_mask]
        a_galaxies = [a_Mcz_prop[:, 1], a_Mcz_prop[:, 2]]

        a_galaxies_array = np.array(a_galaxies)
        a_mean = a_galaxies_array.mean(axis=1)
        a_var = a_galaxies_array.var(axis=1)

        a_observations = [len(a_galaxies[0]), len(a_galaxies[1])]

        density = len(pos_range[0]) / (x_range * y_range)
        a_x_range = min(a_galaxies[0]) - max(a_galaxies[0])
        a_y_range = min(a_galaxies[1]) - max(a_galaxies[1])

        return density
        a_density = len(a_galaxies[0]) / (a_x_range * a_y_range)

        return {"observations": a_observations, "mean": a_mean, "var": a_var, "density": a_density}

    def average_size(self):
        values = []
        """
        No statistical significance in the difference of mean galaxy sizes when analysing through unpaired t-test
            regardless of assumption regarding equal variances.
        :return: {"mean": mean_average, "stv": standard_dev, "t_test": t_stat}
                 or {"mean": mean_average, "stv": standard_dev}
        """

        a_values = []
        for i in self.Mcz_prop:
            if self.min_z < i[0] < self.max_z:
                values.append(i[3])
        return sum(values)/len(values)
            if self.a_min_z < i[0] < self.a_max_z:
                a_values.append(abs(i[3]))
        mean_average = np.mean(a_values)
        var = np.var(a_values)
        observations = [len(a_values[0]), len(a_values[1])]
        df = [len(a_values[0]) - 1, len(a_values[1]) - 1]

        if self.b_min_z is not None and self.b_max_z is not None:
            b_values = []
            for i in self.Mcz_prop:
                if self.b_min_z < i[0] < self.b_max_z:
                    b_values.append(abs(i[3]))
            t_stat = scipy.ttest_ind(a_values, b_values, equal_var=True)

            return {"observations": observations, "df": df, "mean": mean_average, "var": var, "t_test": t_stat}
        else:
            return {"observations": observations, "df": df, "mean": mean_average, "var": var}

    def average_maj_min_axis(self, equal_var=False):
        """

        :param equal_var:
        :return:
        """
        a_minaxis_values = []
        a_majaxis_values = []
        for i in self.Mcz_prop:
            if self.a_min_z < i[0] < self.a_max_z:
                a_minaxis_values.append(i[4])
        for i in self.Mcz_prop:
            if self.a_min_z < i[0] < self.a_max_z:
                a_majaxis_values.append(i[5])
        minaxis_mean_average = np.mean(a_minaxis_values)
        minaxis_standard_dev = np.std(a_minaxis_values)
        majaxis_mean_average = np.mean(a_majaxis_values)
        majaxis_standard_dev = np.std(a_majaxis_values)

        if self.b_min_z is not None and self.b_max_z is not None:
            b_minaxis_values = []
            b_majaxis_values = []
            for i in self.Mcz_prop:
                if self.b_min_z < i[0] < self.b_max_z:
                    b_minaxis_values.append(i[4])
            for i in self.Mcz_prop:
                if self.b_min_z < i[0] < self.b_max_z:
                    b_majaxis_values.append(i[5])
            minaxis_t_stat = scipy.ttest_ind(a_minaxis_values, b_minaxis_values, alternative="less")
            majaxis_t_stat = scipy.ttest_ind(a_majaxis_values, b_majaxis_values, alternative="less")

            return {
                "min_axis": {"mean": minaxis_mean_average, "stv": minaxis_standard_dev, "t_test": minaxis_t_stat},
                "maj_axis": {"mean": majaxis_mean_average, "stv": majaxis_standard_dev, "t_test": majaxis_t_stat}
            }

        else:
            return {
                "min_axis": {"mean": minaxis_mean_average, "stv": minaxis_standard_dev},
                "maj_axis": {"mean": majaxis_mean_average, "stv": majaxis_standard_dev}
            }

    def average_DL(self):
        a_values = []
        for i in self.Mcz_prop:
            if self.a_min_z < i[0] < self.a_max_z:
                a_values.append(abs(i[6]))
        mean_average = np.mean(a_values)
        standard_dev = np.std(a_values)

        if self.b_min_z is not None and self.b_max_z is not None:
            b_values = []
            for i in self.Mcz_prop:
                if self.b_min_z < i[0] < self.b_max_z:
                    b_values.append(abs(i[6]))
            t_stat = scipy.ttest_ind(a_values, b_values, equal_var=True)

            return {"mean": mean_average, "stv": standard_dev, "t_test": t_stat}
        else:
            return {"mean": mean_average, "stv": standard_dev}

class Regression(_Data):

class Regression(_COMBO_Data):
    def __init__(self, test_size, random_state=None):
        _Data.__init__(self)
        """
        This contains all regression analysis applied to the data. This initialise method creates all required arrays
        (test and training) that will be required for the regression analysis.
        :param test_size: The percentage of the parent array that the test array is taken from
        :param random_state: The random seed given to the regression model
        """
        _COMBO_Data.__init__(self)
        self.X_train, self.X_test = train_test_split(
            self.Incl_Mcz_Sloan,
            self.Excl_Mcz_Johnson,
            test_size=test_size,
            random_state=random_state
        )
        self.y_train, self.y_test = train_test_split(
            self.Mcz,
            test_size=test_size,
            random_state=random_state
        )

    def polynomial(self, degree: int, save: bool = True, include_bias: bool = False):
        """
        Constructs polynomial regression line with degree: degree. No significant relationships drawn from this.
        :param save:
        :param save: Boolean controls whether the model is saved to a file or not. (True = Save, False = Not Save)
        :param degree: Degree of the polynomial regression line
        :param include_bias: Dets the coefficients of certain variables to form a certain intercept.
        :return: type:list -> [regression model, regression score]
        """
        poly = PolynomialFeatures(degree=degree, include_bias=include_bias)
        _x_train = poly.fit_transform(self.X_train)
        _x_test = poly.fit_transform(self.X_test)
        reg = LinearRegression()
        reg.fit(_x_train, y=self.y_train)
        score = reg.score(_x_test, self.y_test)
        print(score)
        predicted = reg.predict(_x_test)
        if save:
            pkl.save_model(model=reg, name="polynomial_reg")
        return reg
        return [reg, score]

    def linear(self, save: bool = True):
        """
        Runs a linear regression analysis. No significance given by score.
        :return: type:list -> [regression model, regression score]
        Runs a linear regression analysis.
        :param save: Boolean controls whether the model is saved to a file or not. (True = Save, False = Not Save)
        :return: Linear regression model
        """
        reg = LinearRegression().fit(self.X_train, self.y_train)
        if save:
            pkl.save_model(model=reg, name="linear_reg")
        return reg


class Cluster(_Data):
class Cluster(_COMBO_Data):
    def __init__(self):
        _Data.__init__(self)
        self.X_train = self.Incl_Mcz
        """
        This contains all cluster analysis applied to the data. This initialise method creates all required arrays
        that will be required for the cluster modelling.
        """
        _COMBO_Data.__init__(self)
        self.X_train = self.Incl_Mcz_Johnson

    def kmeans(self, n, save: bool = True):
        """
        This method creates a cluster analysis including the redshift variable
            3-4 is the optimum grouping
        :param save:
        :param save: Boolean controls whether the model is saved to a file or not. (True = Save, False = Not Save)
        :param n: Number of CLuster Groups
        :return: None
        :return: Cluster model
        """
        model = KMeans(n_clusters=n)
        model.fit(X=self.X_train)
        # y_predict = model.predict(X=self.X_test)  # TODO: add method to evaluate accuracy of prediction
        if save:
            pkl.save_model(model=model, name=f"kmeans_n-clusters={n}")

        return model

    def optics(self, save: bool = True):
        model = OPTICS()
        model.fit(X=self.X_train)
        if save: pkl.save_model(model=model, name=f"OPTICS")
        return model


class ManualLabour(object):
    @staticmethod
    def best_model(n_iterations, n_clusters, save: bool = True):
        """
        Function to optimise the random_state for the cluster
        :param save:
        :param n_iterations: Number of initialisations of the cluster model
        :param n_clusters: Number of cluster groups in each iteration
        :return: optimum cluster model
        """
        best_model = [None, None, 0]
        logs = {}
        for x in range(0, n_iterations):
            initialised_class = Cluster()
            model = initialised_class.kmeans(n=n_clusters, save=False)

            current_score = metrics(class_instance=initialised_class, model=model).silhouette(generate_graph=False)
            if current_score > best_model[2]:
                best_model = [initialised_class, model, current_score]
                logs[x] = ["best", best_model[2]]
            else:
                logs[x] = "not best"
            print(x)

        if save:
            pkl.save_model(model=best_model[1], name=f"kmeans_best_n-clusters-{n_clusters}_n-iterations-{n_iterations}")

        return best_model, logs

    @staticmethod
    def Excel_Export(array, workbook_name):
        """
        Exports an array to a excel workbook name given by the parameter Workbook_Name
        :param array: Numpy Array
        :param workbook_name: Name given to the excel workbook
        :return: None
        """
        workbook = xlsxwriter.Workbook(f'{workbook_name}.xlsx')
        worksheet = workbook.add_worksheet()

        row = 0

        for col, data in enumerate(array):
            worksheet.write_column(row, col, data)

        workbook.close()

        return None


if __name__ == "__main__":
    print(Properties(min_redshift=0.73197994, max_redshift=0.77197994).density())
    print(Properties(min_redshift=0.13862278, max_redshift=0.17862278).density())
    print(Properties(min_redshift=0.83964487, max_redshift=0.87964487).density())
    Environment([0.459307, 0.499307], [0.981417, 1.021417]).density_graph()

