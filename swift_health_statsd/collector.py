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

import types

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

    def run(self):
        """ Collect and return a dict with the values of all gauges. """
        self.prepare()
        self.__log = self.logger()
        self.__metric_count = 0
        # TODO: dimensions?

        result = {}
        for metric in self.GAUGES:
            self.__log.debug("Checking metric {0}".format(metric))

            value  = eval("self." + metric + "()")
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

        self.__log.info("Submitted {} metrics".format(self.__metric_count))

    def __submit_gauge(self, metric, value):
        assert(type(value) in (types.IntType, types.LongType, types.FloatType))
        self.__log.debug("Sending {0}={1}".format(metric, value))
        self.__metric_count += 1
        # TODO: actually do something
