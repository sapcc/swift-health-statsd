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

    def collect(self):
        cmd = " ".join((self.config.dispersion_report_path, '-j'))
        out = check_output(cmd, timeout=30)

        # swift-dispersion-report on Liberty prints an initial line "Using
        # storage policy: default", so look for the first line that contains
        # the actual JSON
        while "\n" in out and not out.lstrip().startswith('{'):
            # remove first line
            out = out.split("\n", 1).pop()

        data = json.loads(out)

        for server in ['object', 'container']:
            counts   = data.get(server, {})
            expected = counts.get('copies_expected')
            found    = counts.get('copies_found')

            if expected is None or found is None:
                missing = None
            else:
                missing = expected - found

            self.submit(server + '_copies_expected', expected)
            self.submit(server + '_copies_found',    found)
            self.submit(server + '_copies_missing',  missing)
            self.submit(server + '_overlapping', counts.get('overlapping'))
