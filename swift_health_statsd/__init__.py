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

import logging
import os
import sys

from statsd import StatsClient

from swift_health_statsd.collector  import CollectorConfig
from swift_health_statsd.dispersion import SwiftDispersionCollector
from swift_health_statsd.recon      import SwiftReconCollector

def main():
    log_level = os.getenv("LOG_LEVEL", "warn").upper()
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s: %(message)s")

    # initialize collector config
    add_hostname_suffix = os.getenv("ADD_HOSTNAME_SUFFIX", "false") == "true"
    config = CollectorConfig(
        recon_path             = os.getenv("SWIFT_RECON", "swift-recon"),
        dispersion_report_path = os.getenv("SWIFT_DISPERSION_REPORT",
                                           "swift-dispersion-report"),
        add_hostname_suffix    = add_hostname_suffix,
    )

    # initialize statsd client
    statsd = StatsClient(
        host = os.getenv("STATSD_HOST", "localhost"),
        port = int(os.getenv("STATSD_PORT", "8125")),
    )

    # run collectors
    ok = True
    for collector_class in [SwiftReconCollector, SwiftDispersionCollector]:
        if not collector_class(config).run(statsd):
            ok = False

    if not ok:
        sys.exit(1)
