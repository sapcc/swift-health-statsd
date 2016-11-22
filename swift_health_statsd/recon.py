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

import ast
import logging
import os
import re
import subprocess
import time

from swift_health_statsd.collector import Collector

log = logging.getLogger(__name__)

class SwiftReconCollector(Collector):

    def metric_name_prefix(self):
        return "swift_cluster"

    def logger(self):
        return log

    GAUGES = [
        "storage_used_bytes",
        "storage_free_bytes",
        "storage_capacity_bytes",
        "storage_used_percent",
        "md5_ring_matched",
        "md5_ring_not_matched",
        "md5_ring_errors",
        "md5_ring_all",
        "md5_swiftconf_matched",
        "md5_swiftconf_not_matched",
        "md5_swiftconf_errors",
        "md5_swiftconf_all",
        "containers_updater_sweep_time",
        "objects_updater_sweep_time",
        "objects_replication_duration",
        "objects_replication_age",
        "containers_replication_duration",
        "containers_replication_age",
        "accounts_replication_duration",
        "accounts_replication_age",
        "drives_audit_errors",
        "drives_unmounted",
        "objects_quarantined",
        "containers_quarantined",
        "accounts_quarantined",
    ]

    def prepare(self):
        self.diskusage = {}
        self.md5 = {}
        self.replication_times = {}
        self.quarantined_things = {}

    def swift_recon(self, *params):
        executable = os.getenv('SWIFT_RECON', 'swift-recon')
        cmd = " ".join((executable, " ".join(params)))
        return subprocess.check_output(cmd, shell=True, universal_newlines=True)

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
        return result

    ############################################################################
    # helpers for parsing output of swift-recon

    def get_diskusage(self):
        if not self.diskusage:
            result = self.swift_recon("--diskusage")
            for line in result.splitlines():
                m = re.match(r'Disk usage: space (\w+): (\d+) of (\d+)', line)
                if m:
                    if m.group(1) == 'used':
                        self.diskusage['used'] = long(m.group(2))
                        self.diskusage['capacity'] = long(m.group(3))
                        self.diskusage['used_percent'] = float(self.diskusage['used']) / self.diskusage['capacity']
                    elif m.group(1) == 'free':
                        self.diskusage['free'] = long(m.group(2))
                else:
                    continue
        if not self.diskusage:
            log.error("swift-recon --diskusage did not return any usable output!")
        return self.diskusage

    def get_md5(self):
        if not self.md5:
            result = self.swift_recon("--md5")
            kind = 'undef'
            for line in result.splitlines():
                m = re.match(r'.* Checking ([\.a-zA-Z0-9_]+) md5sum', line)
                if m:
                    kind = m.group(1).replace(".", "")
                    self.md5[kind] = {}
                    continue
                pattern = (r"(\d+)/(\d+) hosts matched, (\d+) error\[s\] "
                           "while checking hosts")
                m = re.match(pattern, line)
                if m:
                    self.md5[kind]['matched'] = int(m.group(1))
                    self.md5[kind]['not_matched'] = (int(m.group(2)) -
                                                     int(m.group(1)))
                    self.md5[kind]['errors'] = int(m.group(3))
                    self.md5[kind]['all'] = (self.md5[kind]['matched'] +
                                             self.md5[kind]['not_matched'] +
                                             self.md5[kind]['errors'])
                else:
                    continue
        return self.md5

    def get_updater_sweeps(self, server_type):
        data = self.swift_recon_parse(server_type, "--updater")
        key = server_type + "_updater_sweep"
        return {hostname: data[hostname][key] for hostname in data}

    def get_replication(self, server_type):
        if server_type in self.replication_times:
            return self.replication_times[server_type]

        # https://twitter.com/stefanmajewsky/status/654660805607096322
        if server_type == "object":
            duration_key, last_key = "object_replication_time", "object_replication_last"
        else:
            duration_key, last_key = "replication_time", "replication_last"

        current_timestamp = time.time()
        data = self.swift_recon_parse(server_type, "--replication")
        result = {"duration": {}, "age": {}}
        for hostname in data:
            if data[hostname][duration_key] is not None:
                result["duration"][hostname] = data[hostname][duration_key]
                # convert timestamp of last completion into an age
                result["age"][hostname] = current_timestamp - data[hostname][last_key]

        self.replication_times[server_type] = result
        return result

    def get_unmounted_drives(self):
        data = self.swift_recon_parse("--unmounted")
        return {hostname: len(data[hostname]) for hostname in data}

    def get_drive_audit_errors(self):
        data = self.swift_recon_parse("--driveaudit")
        return {hostname: data[hostname]['drive_audit_errors'] for hostname in data}

    def get_quarantined(self):
        if not self.quarantined_things:
            data = self.swift_recon_parse("--quarantined")
            for hostname in data:
                for key in data[hostname]:
                    self.quarantined_things.setdefault(key, {})[hostname] = data[hostname][key]
        return self.quarantined_things

    ############################################################################
    # helpers for accessing parsed output of swift-recon

    def storage(self, value):
        self.get_diskusage()
        if value in self.diskusage:
            return self.diskusage[value]

    def consistency(self, kind, value):
        self.get_md5()
        if kind in self.md5:
            if value in self.md5[kind]:
                return self.md5[kind][value]

    def replication(self, server_type, value):
        data = self.get_replication(server_type)
        if value in data:
            return data[value]

    def quarantined(self, value):
        data = self.get_quarantined()
        if value in data:
            return data[value]

    ############################################################################
    # one method for each exposed metric

    # storage capacity

    def storage_free_bytes(self):
        return self.storage('free')

    def storage_used_bytes(self):
        return self.storage('used')

    def storage_capacity_bytes(self):
        return self.storage('capacity')
    
    def storage_used_percent(self):
        return self.storage('used_percent')

    # configuration consistency

    def md5_ring_matched(self):
        return self.consistency('ring', 'matched')

    def md5_ring_not_matched(self):
        return self.consistency('ring', 'not_matched')

    def md5_ring_errors(self):
        return self.consistency('ring', 'errors')

    def md5_ring_all(self):
        return self.consistency('ring', 'all')

    def md5_swiftconf_matched(self):
        return self.consistency('swiftconf', 'matched')

    def md5_swiftconf_not_matched(self):
        return self.consistency('swiftconf', 'not_matched')

    def md5_swiftconf_errors(self):
        return self.consistency('swiftconf', 'errors')

    def md5_swiftconf_all(self):
        return self.consistency('swiftconf', 'all')

    # eventual consistency 1: updater sweep timings

    def containers_updater_sweep_time(self):
        return self.get_updater_sweeps('container')

    def objects_updater_sweep_time(self):
        return self.get_updater_sweeps('object')

    # eventual consistency 2: replication timings

    def objects_replication_duration(self):
        return self.replication("object", "duration")

    def objects_replication_age(self):
        return self.replication("object", "age")

    def containers_replication_duration(self):
        return self.replication("container", "duration")

    def containers_replication_age(self):
        return self.replication("container", "age")

    def accounts_replication_duration(self):
        return self.replication("account", "duration")

    def accounts_replication_age(self):
        return self.replication("account", "age")

    # cluster health

    def drives_unmounted(self):
        return self.get_unmounted_drives()

    def drives_audit_errors(self):
        return self.get_drive_audit_errors()

    def objects_quarantined(self):
        return self.quarantined("objects")

    def containers_quarantined(self):
        return self.quarantined("containers")

    def accounts_quarantined(self):
        return self.quarantined("accounts")
