#!/usr/bin/env python3
"""
This script is written to automate the process of running multiple
Fio benchmarks. The output of the benchmarks have been tailored to be used with
fio-plot.

You may also an older script already part of Fio if that better suits your needs:
https://github.com/axboe/fio/blob/master/tools/genfio
The output of this tool may not always fit with the file-name requirements of
fio-plot, depending on the graph type.
"""

import sys
from .benchlib import (
    checks,
    display,
    runfio,
    supporting,
    argparsing,
    defaultsettings as defaults
)

def main():
    checks.check_encoding()
    settings = defaults.get_default_settings()
    args = argparsing.check_args(settings)
    customsettings = vars(args)
    settings = {**settings, **customsettings}
    defaults.check_settings(settings)
    tests = supporting.generate_test_list(settings)
    display.display_header(settings, tests)
    runfio.run_benchmarks(settings, tests)
