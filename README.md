# swift-health-statsd

This repository contains a small Python program that will scrape metrics from
the output of `swift-dispersion-report` and `swift-recon`, and submit these to
a StatsD endpoint.

# Installation

Like any other setuptools-based Python 2 program, for example:

```bash
pip install git+https://github.com/sapcc/swift-health-statsd
```

Python 3 might also work, but has not been tested. (Feedback is appreciated.)

# Usage

Run the `swift-health-statsd` program from your `$PATH` or, if installed into a
virtualenv, from the virtualenv's `bin` directory. The following environment variables are recognized:

| Key | Default | Explanation |
|-----|---------|-------------|
| `LOG_LEVEL` | `warn` | Log level. Set to `info` to get a short report when metrics are sent, set to `debug` to see all metric names and values that are sent. |
| `STATSD_HOST` | `localhost` | Host where statsd is running. |
| `STATSD_PORT` | `8125` | Port where statsd is running. |
| `SWIFT_RECON` | `swift-recon` | Path to the `swift-recon` executable. |
| `SWIFT_DISPERSION_REPORT` | `swift-dispersion-report` | Path to the `swift-dispersion-report` executable. |
