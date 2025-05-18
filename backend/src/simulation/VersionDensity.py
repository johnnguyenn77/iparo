import random
import time
from abc import abstractmethod, ABC
from enum import IntEnum

import numpy as np
from src.simulation.IPARO import IPARO
from src.simulation.TimeUnit import TimeUnit


class VersionVolume(IntEnum):
    """
    The version volume class is determined roughly by the number of nodes to test.
    """
    SINGLE = 1
    SMALL = 10
    MEDIUM = 100
    LARGE = 1000
    HYPER_LARGE = 10000


class VersionDensity(ABC):

    @abstractmethod
    def __str__(self):
        """
        Used for naming a version density.
        """
        pass

    @abstractmethod
    def sample(self, n: int) -> np.ndarray:
        """
        Samples n times
        :param n: The number of times to sample
        :returns: An n-element ``numpy`` array containing the samples.
        """
        pass


class IntervalVersionDensity(VersionDensity, ABC):
    """
    A class that inherits from VersionDensity by adding the interval attribute.
    """

    def __init__(self, interval: float = 1000):
        self._interval = interval


class VersionGenerator:
    """
    The version generator determines how the densities are to be generated.
    """

    def __init__(self, density: VersionDensity):
        """
        Initializes with a generator.
        """
        self.density = density
        self.start_time = int(time.time() * TimeUnit.SECONDS)

    def generate(self, n: int, url: str = "example.com") -> list[IPARO]:
        timestamps = np.sort(np.int64(self.start_time + self.density.sample(n)))
        contents = [bytes([random.randint(32, 126) for _ in range(100)]) for _ in range(n)]
        iparo = [IPARO(url=url, timestamp=timestamp, linked_iparos=set(), seq_num=-1, content=iparo_content)
                 for (timestamp, iparo_content) in zip(timestamps, contents)]
        return iparo


class UniformVersionDensity(IntervalVersionDensity):

    def __init__(self, interval: float = 1000):
        super().__init__(interval)

    def __str__(self):
        return "Uniform"

    def sample(self, n: int):
        return np.random.uniform(high=self._interval, size=n)


class LinearVersionDensity(IntervalVersionDensity):
    """
    The number of nodes per unit time ``t`` is a function ``f(t) = a*t+b.`` where ``0 <= b <= 1``
    and ``0 <= t <= 1``.
    """

    def __str__(self):
        return "Linear"  # Might change later

    def __init__(self, slope: float, interval: float = 1000):
        """
        Constructor
        :param slope: A number between -2 and 2, referring to the linear coefficient of the PDF.
        :param interval: The time interval.
        """
        super().__init__(interval)
        self.slope = slope

    def sample(self, n: int):
        # Probability of generating the triangular distribution.
        # If negative, choose the triangular distribution with mode 0,
        # if positive, choose the triangular distribution with mode self._interval.
        interval = self._interval
        weight_triangular = self.slope / 2
        probabilities = np.array([1 - abs(weight_triangular),
                                  max(weight_triangular, 0),
                                  max(-weight_triangular, 0)])

        chosen_distributions = np.random.choice(3, size=n,
                                                p=probabilities)
        choices = np.vstack((np.random.uniform(high=interval, size=n),
                            np.random.triangular(left=0, mode=interval, right=interval, size=n),
                            np.random.triangular(left=0, mode=0, right=interval, size=n)))

        results = choices[chosen_distributions, np.arange(n)]
        return results


class BigHeadLongTailVersionDensity(IntervalVersionDensity):
    """
    Generates a reciprocal distribution as the probability density function.
    """

    def __str__(self):
        return "BHLT"  # Might change later

    def __init__(self, param: float, interval: float = 1000):
        """
        :param param: The parameter that is a positive number not equal to 1.
        """
        super().__init__(interval)
        self.param = param

    def sample(self, n: int):
        uniform_random_numbers = np.random.uniform(size=n)
        result = self._interval * (self.param ** uniform_random_numbers - 1) / (self.param - 1)
        return result


class MultipeakVersionDensity(VersionDensity):
    """
    A distribution with multiple peaks. For this version, I will use a normal distribution
    with varying standard deviations.
    """

    def __str__(self):
        return "Multipeak"  # Might change later

    def __init__(self, weights: np.ndarray, distributions: np.ndarray):
        """
        Constructor

        :param weights: The weights (which must be non-negative)
        :param distributions: An array that is N x 2, where N is the number of weights.
        The first column contains all the means, and the second column contains all the standard
        deviations.


        """
        self.weights = weights
        self.distributions = distributions

    def sample(self, n: int):
        n_distributions = len(self.distributions)

        # Make an array of all the possible distributions
        arr = np.zeros((n_distributions, n))
        for i in range(n_distributions):
            mu, sigma = self.distributions[i, :]
            arr[i, :] = np.random.normal(loc=mu, scale=sigma, size=n)

        # Normalize
        self.weights /= np.sum(self.weights)
        choices = np.random.choice(np.arange(n_distributions), size=n, p=self.weights)
        results = arr[choices, np.arange(n)]

        return results
