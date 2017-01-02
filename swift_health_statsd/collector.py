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
import os

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
        self.__skipped_count = 0
        self.__statsd = statsd
        with_hostnames = os.getenv('ADD_HOSTNAME_SUFFIX', 'false') == 'true'

        result = {}
        for metric in self.GAUGES:
            self.__log.debug("Checking metric {0}".format(metric))

            value = getattr(self, metric)()
            metric = ".".join([self.metric_name_prefix(), metric])

            # value may be a dictionary with values by storage node
            if isinstance(value, dict):
                # since StatsD has no concept of labels (like in Prometheus) or
                # dimensions (like in Monasca), we just discard the hostname
                # here and submit the values individually, so that max/min/avg
                # will still work as expected...
                for hostname in value:
                    # ...unless the caller advised us to include the hostname
                    # in the label name
                    this_metric = metric
                    if with_hostnames:
                        this_metric = "{}.from.{}".format(metric, hostname)
                    self.__submit_gauge(this_metric, value[hostname])
            else:
                self.__submit_gauge(metric, value)

        self.__log.info("Submitted {} {} metrics ({} skipped)"
            .format(self.__metric_count,
                    self.metric_name_prefix(),
                    self.__skipped_count))

    def __submit_gauge(self, metric, value):
        # skip metric if no useful value was provided
        if value is None:
            self.__log.debug("Not sending {0} = None".format(metric))
            self.__skipped_count += 1
            return

        self.__log.debug("Sending {0} = {1}".format(metric, value))
        assert isinstance(value, numbers.Real)
        self.__metric_count += 1
        self.__statsd.gauge(metric, value)
