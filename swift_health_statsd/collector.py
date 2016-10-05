# Copyright 2016 SAP SE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numbers

class Collector(object):
    """ Subclasses of this implement collection of a certain type of metrics.
        Subclasses must:
        * implement logger(), metric_name_prefix() and optionally prepare()
        * have an array GAUGES containing valid StatsD metric names
        * implement methods for each gauge (with method name = metric name)
          that return the current value of the gauge
    """

    def prepare(self):
        """ Can be overridden by subclass to perform setup at the start of a
            check() run.
        """
        pass

    def logger(self):
        """ Must be overridden by subclass to return its logger instance. """
        raise NotImplementedError

    def metric_name_prefix(self):
        """ Must be overridden by subclass to return a common prefix for metric
            names in this collector.
        """
        raise NotImplementedError

    def run(self, statsd):
        """ Collect and return a dict with the values of all gauges. Takes a
            statsd.StatsClient instance.
        """
        self.prepare()
        self.__log = self.logger()
        self.__metric_count = 0
        self.__statsd = statsd

        result = {}
        for metric in self.GAUGES:
            self.__log.debug("Checking metric {0}".format(metric))

            value = getattr(self, metric)()
            metric = "_".join([self.metric_name_prefix(), metric])

            # value may be a dictionary with values by storage node
            if isinstance(value, dict):
                # since StatsD has no concept of labels (like in Prometheus) or
                # dimensions (like in Monasca), we just discard the hostname
                # here and submit the values individually, so that max/min/avg
                # will still work as expected
                for hostname in value:
                    self.__submit_gauge(metric, value[hostname])
            else:
                self.__submit_gauge(metric, value)

        self.__log.info("Submitted {} {} metrics"
            .format(self.__metric_count, self.metric_name_prefix()))

    def __submit_gauge(self, metric, value):
        # sometimes swift-recon just throws None at us when it really means 0,
        # but we should not crash over this (link is relevant:
        # https://twitter.com/stefanmajewsky/status/778575829668421632)
        if value is None:
            value = 0

        self.__log.debug("Sending {0} = {1}".format(metric, value))
        assert isinstance(value, numbers.Real)
        self.__metric_count += 1
        self.__statsd.gauge(metric, value)
