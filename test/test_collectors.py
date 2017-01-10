# Copyright 2017 SAP SE
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

from swift_health_statsd.collector  import CollectorConfig
from swift_health_statsd.recon      import SwiftReconCollector
from swift_health_statsd.dispersion import SwiftDispersionCollector

import time

def expected_gauges_dispersion():
    return {
        "swift_dispersion.container_copies_expected": 120,
        "swift_dispersion.container_copies_found": 120,
        "swift_dispersion.container_copies_missing": 0,
        "swift_dispersion.container_overlapping": 0,
        "swift_dispersion.object_copies_expected": 1965,
        "swift_dispersion.object_copies_found": 1965,
        "swift_dispersion.object_copies_missing": 0,
        "swift_dispersion.object_overlapping": 0,
    }

def expected_gauges_recon():
    return {
        # from test/fixtures/recon_account_replication
        "swift_cluster.accounts_replication_age.from.10.0.0.1": 32.4190309047699,
        "swift_cluster.accounts_replication_age.from.10.0.0.2": 30.34965205192566,
        "swift_cluster.accounts_replication_age.from.10.0.0.3": 12.076211929321289,
        "swift_cluster.accounts_replication_age.from.10.0.0.4": 34.27333211898804,
        "swift_cluster.accounts_replication_age.from.10.0.0.5": 19.855139017105103,
        "swift_cluster.accounts_replication_age.from.10.0.0.6": 19.954685926437378,
        "swift_cluster.accounts_replication_age.from.10.0.0.7": 32.175179958343506,
        "swift_cluster.accounts_replication_age.from.10.0.0.8": 29.634557008743286,
        "swift_cluster.accounts_replication_age.from.10.0.0.9": 27.16282296180725,
        "swift_cluster.accounts_replication_duration.from.10.0.0.1": 0.22192907333374023,
        "swift_cluster.accounts_replication_duration.from.10.0.0.2": 0.21590185165405273,
        "swift_cluster.accounts_replication_duration.from.10.0.0.3": 0.2853360176086426,
        "swift_cluster.accounts_replication_duration.from.10.0.0.4": 0.29166078567504883,
        "swift_cluster.accounts_replication_duration.from.10.0.0.5": 0.2945420742034912,
        "swift_cluster.accounts_replication_duration.from.10.0.0.6": 0.3072531223297119,
        "swift_cluster.accounts_replication_duration.from.10.0.0.7": 0.28057312965393066,
        "swift_cluster.accounts_replication_duration.from.10.0.0.8": 0.4204409122467041,
        "swift_cluster.accounts_replication_duration.from.10.0.0.9": 1.8770229816436768,

        # from test/fixtures/recon_container_replication
        "swift_cluster.containers_replication_age.from.10.0.0.1": 36.81415796279907,
        "swift_cluster.containers_replication_age.from.10.0.0.2": 37.084654092788696,
        "swift_cluster.containers_replication_age.from.10.0.0.3": 34.84430289268494,
        "swift_cluster.containers_replication_age.from.10.0.0.4": 33.71821093559265,
        "swift_cluster.containers_replication_age.from.10.0.0.5": 40.163285970687866,
        "swift_cluster.containers_replication_age.from.10.0.0.6": 10.69006609916687,
        "swift_cluster.containers_replication_age.from.10.0.0.7": 31.308770895004272,
        "swift_cluster.containers_replication_age.from.10.0.0.8": 11.902982950210571,
        "swift_cluster.containers_replication_age.from.10.0.0.9": 17.679863929748535,
        "swift_cluster.containers_replication_duration.from.10.0.0.1": 1.8265631198883057,
        "swift_cluster.containers_replication_duration.from.10.0.0.2": 2.0269689559936523,
        "swift_cluster.containers_replication_duration.from.10.0.0.3": 2.1620051860809326,
        "swift_cluster.containers_replication_duration.from.10.0.0.4": 2.055312156677246,
        "swift_cluster.containers_replication_duration.from.10.0.0.5": 1.9019739627838135,
        "swift_cluster.containers_replication_duration.from.10.0.0.6": 1.7866718769073486,
        "swift_cluster.containers_replication_duration.from.10.0.0.7": 1.987098217010498,
        "swift_cluster.containers_replication_duration.from.10.0.0.8": 4.202234983444214,
        "swift_cluster.containers_replication_duration.from.10.0.0.9": 17.74868607521057,

        # from test/fixtures/recon_container_updater
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.1": 3.276121139526367,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.2": 3.072524070739746,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.3": 3.0345959663391113,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.4": 3.258327007293701,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.5": 3.1556501388549805,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.6": 3.089754819869995,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.7": 3.0257790088653564,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.8": 5.448167085647583,
        "swift_cluster.containers_updater_sweep_time.from.10.0.0.9": 15.271306037902832,

        # from test/fixtures/recon_diskusage
        "swift_cluster.storage_capacity_bytes": 758939469635584,
        "swift_cluster.storage_free_bytes": 634467918188544,
        "swift_cluster.storage_used_bytes": 124471551447040,
        "swift_cluster.storage_used_percent": 0.16400721852930755,

        # from test/fixtures/recon_driveaudit
        "swift_cluster.drives_audit_errors.from.10.0.0.1": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.2": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.3": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.4": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.5": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.6": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.7": 1,
        "swift_cluster.drives_audit_errors.from.10.0.0.8": 0,
        "swift_cluster.drives_audit_errors.from.10.0.0.9": 0,

        # from test/fixtures/recon_md5
        "swift_cluster.md5_ring_all": 9,
        "swift_cluster.md5_ring_errors": 0,
        "swift_cluster.md5_ring_matched": 9,
        "swift_cluster.md5_ring_not_matched": 0,
        "swift_cluster.md5_swiftconf_all": 9,
        "swift_cluster.md5_swiftconf_errors": 0,
        "swift_cluster.md5_swiftconf_matched": 9,
        "swift_cluster.md5_swiftconf_not_matched": 0,

        # from test/fixtures/recon_object_replication
        "swift_cluster.objects_replication_age.from.10.0.0.1": 216.76890206336975,
        "swift_cluster.objects_replication_age.from.10.0.0.2": 222.42571806907654,
        "swift_cluster.objects_replication_age.from.10.0.0.3": 388.48985290527344,
        "swift_cluster.objects_replication_age.from.10.0.0.4": 418.488981962204,
        "swift_cluster.objects_replication_age.from.10.0.0.5": 291.2628700733185,
        "swift_cluster.objects_replication_age.from.10.0.0.6": 413.4935779571533,
        "swift_cluster.objects_replication_age.from.10.0.0.7": 301.63419699668884,
        "swift_cluster.objects_replication_age.from.10.0.0.8": 102.29441905021667,
        "swift_cluster.objects_replication_age.from.10.0.0.9": 760.5847918987274,
        "swift_cluster.objects_replication_duration.from.10.0.0.1": 6.153176216284434,
        "swift_cluster.objects_replication_duration.from.10.0.0.2": 9.570358582337697,
        "swift_cluster.objects_replication_duration.from.10.0.0.3": 9.101836049556733,
        "swift_cluster.objects_replication_duration.from.10.0.0.4": 9.420962369441986,
        "swift_cluster.objects_replication_duration.from.10.0.0.5": 9.348060735066731,
        "swift_cluster.objects_replication_duration.from.10.0.0.6": 8.945157102743785,
        "swift_cluster.objects_replication_duration.from.10.0.0.7": 6.291674816608429,
        "swift_cluster.objects_replication_duration.from.10.0.0.8": 12.08376603126526,
        "swift_cluster.objects_replication_duration.from.10.0.0.9": 24.81597485144933,

        # from test/fixtures/recon_object_updater
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.1": 0.1995248794555664,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.2": 0.17919588088989258,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.3": 0.18461108207702637,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.4": 0.19096088409423828,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.5": 0.19083690643310547,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.6": 0.1859149932861328,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.7": 0.18849611282348633,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.8": 0.4458739757537842,
        "swift_cluster.objects_updater_sweep_time.from.10.0.0.9": 1.4423089027404785,

        # from test/fixtures/recon_quarantined
        "swift_cluster.accounts_quarantined.from.10.0.0.1": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.2": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.3": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.4": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.5": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.6": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.7": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.8": 0,
        "swift_cluster.accounts_quarantined.from.10.0.0.9": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.1": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.2": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.3": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.4": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.5": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.6": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.7": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.8": 0,
        "swift_cluster.containers_quarantined.from.10.0.0.9": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.1": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.2": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.3": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.4": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.5": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.6": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.7": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.8": 0,
        "swift_cluster.objects_quarantined.from.10.0.0.9": 0,

        # from test/fixtures/recon_unmounted
        "swift_cluster.drives_unmounted.from.10.0.0.1": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.2": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.3": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.4": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.5": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.6": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.7": 1,
        "swift_cluster.drives_unmounted.from.10.0.0.8": 0,
        "swift_cluster.drives_unmounted.from.10.0.0.9": 0,

    }

class MockStatsClient(object):
    """ Drop-in replacement for statsd.StatsClient that collects all the gauge
        values pushed into it into a simple hash.
    """
    def __init__(self):
        self.gauges = {}

    def gauge(self, metric, value):
        self.gauges[metric] = value

def mock_time(timestamp):
    """ Replaces time.time() with a function that always returns the given
        timestamp.
    """
    time.time = lambda: timestamp

def shared_test_setup():
    config = CollectorConfig(
        recon_path             = "./test/fixtures/recon.sh",
        dispersion_report_path = "./test/fixtures/dispersion.sh",
        add_hostname_suffix    = True,
    )
    statsd = MockStatsClient()
    mock_time(1484057460)
    return config, statsd

### unit test entrypoints (found by the "test_" name prefix)

def test_recon():
    config, statsd = shared_test_setup()
    SwiftReconCollector(config).run(statsd)
    assert statsd.gauges == expected_gauges_recon()

def test_dispersion():
    config, statsd = shared_test_setup()
    SwiftDispersionCollector(config).run(statsd)
    assert statsd.gauges == expected_gauges_dispersion()
