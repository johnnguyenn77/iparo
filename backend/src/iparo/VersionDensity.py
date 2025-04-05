from abc import ABC, abstractmethod
import math
import random
from datetime import datetime, timedelta
from enum import IntEnum

from iparo.IPARO import IPARO
from iparo.IPARODateFormat import IPARODateFormat

URL = "example.com"


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
    """
    The version density class determines the "shape" of the graph.
    """

    def __init__(self, interval: timedelta = timedelta(seconds=999999)):
        # Gets the start time, in microseconds. Note that there is 1 underscore to indicate a protected attribute
        # that can be inherited to other classes.
        self._start_time = datetime.now().replace(microsecond=0)
        self._interval = interval

    def get_iparos(self, volume: VersionVolume) -> list[IPARO]:
        """
        Gets the nodes according to a version volume.
        :param volume: The version volume
        :return: The list of unlinked IPAROs
        """
        dq = 1 / (volume - 1) if volume != VersionVolume.SINGLE else 0.0
        iparos = []
        for i in range(volume):
            quantile = i * dq
            interval_frac = self.get_quantile(quantile)
            value = self._interval * interval_frac
            time = self._start_time + value
            time_string = datetime.strftime(time, IPARODateFormat.DATE_FORMAT)
            iparo = IPARO(timestamp=time_string, content=f"Node {i}".encode(), linked_iparos=set(),
                          seq_num=-1, url=URL)
            iparos.append(iparo)

        return iparos

    @abstractmethod
    def get_quantile(self, x: float) -> float:
        pass


class UniformVersionDensity(VersionDensity):
    """
    Uniform version density would mean each node is equally spaced.
    """

    def get_quantile(self, x: float) -> float:
        return x


class LinearVersionDensity(VersionDensity):
    """
    The number of nodes per unit time ``t`` is a function ``f(t) = a*t+b.`` for ``0 <= t <= 1``.
    """

    def __init__(self, slope: float, time_interval: timedelta = timedelta(seconds=999999)):
        """
        Args:
            slope (float): The slope of the underlying linear density function at the beginning.
            time_interval (timedelta): The interval of time.
        """
        super().__init__(time_interval)
        self.slope = slope

    def get_quantile(self, x: float) -> float:
        # Get the quadratic equation: 0 = a*x^2/2 + b*x - c. Reason is F(x) is the integral of f(x) with respect to x.
        a = 2 * (1 - self.slope)
        b = self.slope
        c = x

        # Use the "modified" quadratic formula (-b + sqrt(b^2 + 4(a/2)(-c))) / (2a/2) = (-b + sqrt(b^2 + 2ac)) / a.
        # This is the quadratic function with a' = a/2 and c' = -c
        return (-b + math.sqrt(b ** 2 + 2 * a * c)) / a


class BigHeadLongTailVersionDensity(VersionDensity):
    """
    A big head and long tail distribution. For this version, I will use the modified reciprocal distribution.
    Thus, the CDF is ``F(x) = ln(1+(a-1)x)/ln(a)``, for all ``a != 1`` and ``a > 0``
    """

    def __init__(self, param: float, time_interval: timedelta = timedelta(seconds=999999)):
        """
        Args:
            param (float): The parameter of the underlying reciprocal density function at the beginning.
            time_interval (timedelta): The interval of time.
        """
        super().__init__(time_interval)
        self.param = param

    def get_quantile(self, x: float) -> float:
        # F(x, a) = ln(1+(a-1)x) / ln(a), 0 <= x <= 1, a > 1
        # a^q = e^[ln(a)*ln(1+(a-1)x)/ln(a)]
        # a^q = 1+(a-1)x
        # a^q - 1 = (a-1)x
        # q*ln(a) - 1 = (a-1)x
        # -> F^-1(q, a) = (a^q - 1) / (a-1)
        return (math.pow(self.param, x) - 1) / (self.param - 1)


class MultipeakDensity(VersionDensity):
    """
    A big head and long tail distribution. For this version, I will use a uniform random variable to
    select which normal distribution to use, and then condition a normal random variate from there.
    Unlike the other distributions, this one uses random variates because there is no quantile distribution.
    """

    def __init__(self, probability_weights: list[tuple[float, float, float]],
                 time_interval: timedelta = timedelta(seconds=999999)):
        """
        Args:
            probability_weights (list[tuple[float, float, float]]): The probability weights. The first float represents the probability weight for the uniform random variate. The second float represents the mean of the normal distribution, and the third float represents the standard deviation.
            time_interval (timedelta): The interval of time.
        """
        super().__init__(time_interval)
        self.probability_weights = probability_weights

    def get_iparos(self, volume: VersionVolume) -> list[IPARO]:
        sum_weights = 0
        probs = []
        # Two pass (first to know the sum of the weights
        for weight, _, _ in self.probability_weights:
            sum_weights += weight
            probs.append(sum_weights)

        probs = [weight / sum_weights for weight in probs]
        iparos = []

        for i in range(volume):
            # Random variable 1
            rv1 = random.random()

            # Assumption: probs is sorted
            dist_num = 0
            while probs[dist_num] < rv1:
                dist_num += 1

            # Random variable 2 will determine time of "creation".
            _, mean, sd = self.probability_weights[dist_num]
            td = timedelta(seconds=random.normalvariate(mean, sd))
            time_string = IPARODateFormat.add_timedelta(self._start_time.strftime(IPARODateFormat.DATE_FORMAT), td)
            iparo = IPARO(timestamp=time_string, content=f"Node {i}".encode(),
                          linked_iparos=set(), seq_num=-1, url=URL)

            iparos.append(iparo)

        iparos.sort(key=lambda iparo: iparo.timestamp)
        return iparos

    def get_quantile(self, x: float) -> float:
        pass
