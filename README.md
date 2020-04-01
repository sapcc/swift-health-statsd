# Archived project. No maintenance.

This project is not maintained anymore and is archived. Consider switching to the new [swift-health-exporter](https://github.com/sapcc/swift-health-exporter).

# swift-health-statsd

This repository contains a small Python program that will scrape metrics from
the output of `swift-dispersion-report` and `swift-recon`, and submit these to
a StatsD endpoint.

## Installation

Like any other setuptools-based Python 2 program, for example:

```bash
pip install git+https://github.com/sapcc/swift-health-statsd
```

Python 3 might also work, but has not been tested. (Feedback is appreciated.)

For development, setup a virtualenv and install into there:

```bash
pip install -e .
python setup.py test
```

## Usage

Run the `swift-health-statsd` program from your `$PATH` or, if installed into a
virtualenv, from the virtualenv's `bin` directory. The following environment variables are recognized:

| Key | Default | Explanation |
|-----|---------|-------------|
| `LOG_LEVEL` | `warn` | Log level. Set to `info` to get a short report when metrics are sent, set to `debug` to see all metric names and values that are sent. |
| `STATSD_HOST` | `localhost` | Host where statsd is running. |
| `STATSD_PORT` | `8125` | Port where statsd is running. |
| `SWIFT_RECON` | `swift-recon` | Path to the `swift-recon` executable. |
| `SWIFT_DISPERSION_REPORT` | `swift-dispersion-report` | Path to the `swift-dispersion-report` executable. |
| `ADD_HOSTNAME_SUFFIX` | `false` | If `true`, add a suffix to each metric name that identifies the storage server from which the metric originated. |

`ADD_HOSTNAME_SUFFIX` is useful when the receiver would otherwise only observe the last value for each metric. Here's how metric names are formatted:

```
# example log output with ADD_HOSTNAME_SUFFIX=false (default)
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors = 0
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors = 2
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors = 0

# example log output with ADD_HOSTNAME_SUFFIX=true
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors.from.192.168.0.1 = 0
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors.from.192.168.0.2 = 2
DEBUG:swift_health_statsd.recon:Sending swift_cluster.drives_audit_errors.from.192.168.0.3 = 0
```
