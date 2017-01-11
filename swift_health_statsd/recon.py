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

import ast
import logging
import re
import subprocess
import time

from swift_health_statsd.ipc import check_output
from swift_health_statsd.collector import Collector

log = logging.getLogger(__name__)

class SwiftReconCollector(Collector):

    def metric_name_prefix(self):
        return "swift_cluster"

    def logger(self):
        return log

    def swift_recon(self, *params):
        cmd = " ".join((self.config.recon_path, " ".join(params)))
        return check_output(cmd, timeout=30)

    def swift_recon_parse(self, *params):
        # call swift-recon in verbose mode
        output = self.swift_recon("-v", *params)

        # look for verbose output containing the raw data structures received
        # from the storage nodes
        result = {}
        for line in output.splitlines():
            m = re.match(r'^-> https?://([a-zA-Z0-9-.]+)\S*\s(.*)', line)
            if m:
                log.debug("Output from swift-recon {0}: {1}".format(" ".join(params), line))
                hostname, data_str = m.group(1), m.group(2)
                try:
                    result[hostname] = ast.literal_eval(data_str)
                except (ValueError, SyntaxError):
                    log.error("swift-recon {0} erroneous for node {1}: {2}".format(params, hostname, data_str))
                    continue
        if not result:
            log.error("swift-recon {0} did not return any usable output!".format(params))
            return {}
        return result

    def collect(self):
        # This method is split into multiple subparts (one for each subprocess
        # call to swift-recon) for better readability.
        self.__collect_driveaudit()
        self.__collect_unmounted()
        self.__collect_diskusage()
        self.__collect_md5()
        self.__collect_updater_sweeps()
        self.__collect_replication()
        self.__collect_quarantined()

    ############################################################################
    # subparts of collect()

    def __collect_diskusage(self):
        """ Parser for `swift-recon --diskusage`. """
        data = {}
        for line in self.swift_recon("--diskusage").splitlines():
            m = re.match(r'Disk usage: space (\w+): (\d+) of (\d+)', line)
            if m:
                if m.group(1) == 'used':
                    data['used'] = long(m.group(2))
                    data['capacity'] = long(m.group(3))
                    data['used_percent'] = float(data['used']) / data['capacity']
                elif m.group(1) == 'free':
                    data['free'] = long(m.group(2))
            else:
                continue

        self.submit('storage_free_bytes',     data.get('free'))
        self.submit('storage_used_bytes',     data.get('used'))
        self.submit('storage_capacity_bytes', data.get('capacity'))
        self.submit('storage_used_percent',   data.get('used_percent'))

    def __collect_md5(self):
        """ Parser for `swift-recon --md5`. """
        data = {}
        kind = 'undef'

        for line in self.swift_recon("--md5").splitlines():
            m = re.match(r'.* Checking ([\.a-zA-Z0-9_]+) md5sum', line)
            if m:
                kind = m.group(1).replace(".", "")
                data[kind] = {}
                continue
            pattern = (r"(\d+)/(\d+) hosts matched, (\d+) error\[s\] "
                       "while checking hosts")
            m = re.match(pattern, line)
            if m:
                data[kind]['matched'] = int(m.group(1))
                data[kind]['not_matched'] = (int(m.group(2)) -
                                                 int(m.group(1)))
                data[kind]['errors'] = int(m.group(3))
                data[kind]['all'] = (data[kind]['matched'] +
                                     data[kind]['not_matched'] +
                                     data[kind]['errors'])
            else:
                continue

        for kind in ['ring', 'swiftconf']:
            values = data.get(kind, {})
            for key in ['matched', 'not_matched', 'errors', 'all']:
                metric = "md5_{}_{}".format(kind, key)
                self.submit(metric, values.get(key))

    def __collect_updater_sweeps(self):
        """ Parser for `swift-recon --updater`. """
        for server_type in ['container', 'object']:
            data = self.swift_recon_parse(server_type, "--updater")
            metric = server_type + "s_updater_sweep_time"
            key = server_type + "_updater_sweep"
            for hostname in data:
                self.submit(metric, data[hostname][key], hostname)

    def __collect_replication(self):
        """ Parser for `swift-recon --replication`. """
        for server_type in ['account', 'container', 'object']:
            duration_metric = server_type + "s_replication_duration"
            age_metric = server_type + "s_replication_age"

            # https://twitter.com/stefanmajewsky/status/654660805607096322
            if server_type == "object":
                duration_key, last_key = "object_replication_time", "object_replication_last"
            else:
                duration_key, last_key = "replication_time", "replication_last"

            current_timestamp = time.time()
            data = self.swift_recon_parse(server_type, "--replication")
            for hostname in data:
                self.submit(duration_metric,
                    data[hostname].get(duration_key), hostname)
                # convert timestamp of last completion into an age
                if data[hostname][last_key] is None:
                    continue
                self.submit(age_metric,
                    current_timestamp - data[hostname].get(last_key), hostname)

    def __collect_quarantined(self):
        """ Parser for `swift-recon --quarantined`. """
        data = self.swift_recon_parse("--quarantined")
        for hostname in data:
            values = data[hostname]
            for key in ['accounts', 'containers', 'objects']:
                metric = key + "_quarantined"
                self.submit(metric, values.get(key), hostname)

    def __collect_unmounted(self):
        """ Parser for `swift-recon --unmounted`. """
        data = self.swift_recon_parse("--unmounted")
        for hostname in data:
            self.submit("drives_unmounted", len(data[hostname]), hostname)

    def __collect_driveaudit(self):
        """ Parser for `swift-recon --driveaudit`. """
        data = self.swift_recon_parse("--driveaudit")
        for hostname in data:
            self.submit("drives_audit_errors", data[hostname].get('drive_audit_errors'), hostname)
