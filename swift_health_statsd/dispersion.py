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
import subprocess
import types

log = logging.getLogger(__name__)

class SwiftDispersion(checks.AgentCheck):

    GAUGES = [
        "object.copies_expected",
        "object.copies_found",
        "object.copies_missing",
        "object.overlapping",
        "container.copies_expected",
        "container.copies_found",
        "container.copies_missing",
        "container.overlapping",
    ]

    def swift_dispersion(self):
        executable = 'swift-dispersion-report'
        if 'swift_dispersion' in self.init_config:
            executable = self.init_config['swift_dispersion']

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

        return out

    def check(self, instance):
        dimensions = self._set_dimensions(None, instance)

        swift_dispersion = self.swift_dispersion()
        assert(swift_dispersion)

        dispersion = json.loads(swift_dispersion)
        for metric in self.GAUGES:
            log.debug("Checking metric {0}".format(metric))
            disp_metric = metric.split('.', 1)

            if disp_metric[1] == 'copies_missing':
                value = (dispersion[disp_metric[0]]['copies_expected'] -
                         dispersion[disp_metric[0]]['copies_found'])
            else:
                value = dispersion[disp_metric[0]][disp_metric[1]]

            assert(type(value) in (types.IntType, types.LongType,
                                   types.FloatType))

            metric = self.normalize(metric.lower(), 'swift.dispersion')
            log.debug("Sending {0}={1}".format(metric, value))
            self.gauge(metric, value, dimensions=dimensions)
