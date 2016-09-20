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

import json
import logging
import os
import subprocess

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
        executable = os.getenv('SWIFT_DISPERSION_REPORT', 'swift-dispersion-report')

        cmd = " ".join((executable, '-j'))
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                universal_newlines=True)
        out = "".join(pipe.stdout.readlines())

        # swift-dispersion-report on Liberty prints an initial line "Using
        # storage policy: default", so look for the first line that contains
        # the actual JSON
        while "\n" in out and not out.lstrip().startswith('{'):
            # remove first line
            out = out.split("\n", 1).pop()

        self.out = json.loads(out)
        print("out = {}".format(self.out))

    def object_copies_expected(self):
        return self.out['object']['copies_expected']
    def object_copies_found(self):
        return self.out['object']['copies_found']
    def object_copies_missing(self):
        return self.out['object']['copies_expected'] - self.out['object']['copies_found']
    def object_overlapping(self):
        return self.out['object']['overlapping']
    def container_copies_expected(self):
        return self.out['container']['copies_expected']
    def container_copies_found(self):
        return self.out['container']['copies_found']
    def container_copies_missing(self):
        return self.out['container']['copies_expected'] - self.out['container']['copies_found']
    def container_overlapping(self):
        return self.out['container']['overlapping']
