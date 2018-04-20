# Copyright 2016-2017 SAP SE
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
import sys
import traceback

class CollectorConfig(object):
    """ Helper class for the Collector class that contains its configuration
        options. This is usually initialized from os.getenv(), unless
        we're inside a unit test.
    """

    def __init__(self, **kwargs):
        """ Initializer. Initializes the following fields from kwargs:

            add_hostname_suffix (boolean)
            recon_path          (string)
            dispersion_path     (string)

            The semantics of these fields are equivalent to the environment
            variables noted in the README.md
        """
        self.add_hostname_suffix = kwargs.get("add_hostname_suffix", False)
        self.recon_path = kwargs.get("recon_path", "swift-recon")
        self.dispersion_report_path = kwargs.get("dispersion_report_path",
            "swift-dispersion-report")

class Collector(object):
    """ Subclasses of this implement collection of a certain type of metrics.
        Subclasses must:
        * implement logger(), metric_name_prefix(), collector_steps() and
          optionally prepare()
    """

    def __init__(self, config):
        """ Initializer. Takes a CollectorConfig instance. """
        self.config = config

    def collector_steps(self):
        """ Must be overridden by subclass. Returns a dict mapping step names
        to steps (functions that collect metrics, and submit them by calling
        self.submit() for each metric).
        """
        raise NotImplementedError

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
        self.__log = self.logger()
        self.__metric_count = 0
        self.__skipped_count = 0
        self.__statsd = statsd

        ok = True
        for name, step in self.collector_steps().items():
            try:
                step()
            except:
                ok = False
                self.__log.error("collector \"{}\" failed, detailed exception follows".format(name))
                traceback.print_exc(None, sys.stderr) # logs exception and traceback

        self.__log.info("Submitted {} {} metrics ({} skipped)"
            .format(self.__metric_count,
                    self.metric_name_prefix(),
                    self.__skipped_count))

        return ok and self.__skipped_count == 0

    def submit(self, metric, value, hostname=None):
        """ Call this from collect() to submit a metric value. """
        # since StatsD has no concept of labels (like in Prometheus) or
        # dimensions (like in Monasca), we just discard the hostname
        # here and submit the values individually, so that max/min/avg
        # will still work as expected...
        this_metric = "{}.{}".format(self.metric_name_prefix(), metric)
        if hostname is not None and self.config.add_hostname_suffix:
            # ...unless the caller advised us to include the hostname
            # in the label name
            this_metric = "{}.from.{}".format(this_metric, hostname)

        # skip metric if no useful value was provided
        if value is None:
            self.__log.debug("Not sending {0} = None".format(this_metric))
            self.__skipped_count += 1
            return

        self.__log.debug("Sending {0} = {1}".format(this_metric, value))
        assert isinstance(value, numbers.Real)
        self.__metric_count += 1
        self.__statsd.gauge(this_metric, value)
