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

import json
import logging

from swift_health_statsd.ipc import check_output
from swift_health_statsd.collector import Collector

log = logging.getLogger(__name__)

class SwiftDispersionCollector(Collector):

    def metric_name_prefix(self):
        return "swift_dispersion"

    def logger(self):
        return log

    GAUGES = [
        "object_copies_expected",
        "object_copies_found",
        "object_copies_missing",
        "object_overlapping",
        "container_copies_expected",
        "container_copies_found",
        "container_copies_missing",
        "container_overlapping",
    ]

    def prepare(self):
        cmd = " ".join((self.config.dispersion_report_path, '-j'))
        out = check_output(cmd, timeout=30)

        # swift-dispersion-report on Liberty prints an initial line "Using
        # storage policy: default", so look for the first line that contains
        # the actual JSON
        while "\n" in out and not out.lstrip().startswith('{'):
            # remove first line
            out = out.split("\n", 1).pop()

        self.out = json.loads(out)
        log.debug("output from swift-dispersion-report: {}".format(self.out))

    def get(self, level, metric):
        return self.out.get(level, {}).get(metric, None)

    def object_copies_expected(self):
        return self.get('object', 'copies_expected')
    def object_copies_found(self):
        return self.get('object', 'copies_found')
    def object_copies_missing(self):
        expected = self.get('object', 'copies_expected')
        found    = self.get('object', 'copies_found')
        if expected is None or found is None:
            return None
        else:
            return expected - found
    def object_overlapping(self):
        return self.get('object', 'overlapping')
    def container_copies_expected(self):
        return self.get('container', 'copies_expected')
    def container_copies_found(self):
        return self.get('container', 'copies_found')
    def container_copies_missing(self):
        expected = self.get('container', 'copies_expected')
        found    = self.get('container', 'copies_found')
        if expected is None or found is None:
            return None
        else:
            return expected - found
    def container_overlapping(self):
        return self.get('container', 'overlapping')
