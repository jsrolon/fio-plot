#!/usr/bin/env python3
import subprocess
import sys
import os
import copy
from numpy import linspace
import time
import logging

from . import ( 
    supporting,
    checks
)


logger = logging.getLogger(__name__)


def check_fio_version(settings):
    """The 3.x series .json format is different from the 2.x series format.
    This breaks fio-plot, thus this older version is not supported.
    """

    command = ["fio", "--version"]
    result = run_raw_command(command).stdout
    result = result.decode("UTF-8").strip()
    if "fio-3" in result:
        return True
    elif "fio-2" in result:
        print(f"Your Fio version ({result}) is not compatible. Please use Fio-3.x")
        sys.exit(1)
    else:
        print("Could not detect Fio version.")
        sys.exit(1)


def drop_caches(settings):
    command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
    run_raw_command(command)


def run_raw_command(command, env=None):
    print(command)

    result = subprocess.Popen(
        command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )

    # for fio
    os.sched_setaffinity(result.pid, [x for x in range(0, 35) if x % 2 == 0])
    result.wait()

    if result and result.stdout:
#         stdout = result.stdout.decode("UTF-8").strip()
        logger.info(result.stdout)

    if result.returncode != 0:
#         stderr = result.stderr.decode("UTF-8").strip()
        logger.error(result.stderr)
        if result.returncode != 127 and "is_backend" not in stderr: # ridiculous workaround for spdk fio plugin
            sys.exit(1)

    return result


def run_command(settings, benchmark, command):
    """The .ini templates take their values from environment variables:
    https://fio.readthedocs.io/en/latest/fio_doc.html#environment-variables
    This function obtains all the env vars as a dict, and appends the configuration
    settings from args as env variables as well.
    """
    output_directory = supporting.generate_output_directory(settings, benchmark)
    env = os.environ
    settings = supporting.unpack_custom_env_vars(settings)
    settings = supporting.convert_dict_vals_to_str(settings)
    benchmark = supporting.convert_dict_vals_to_str(benchmark)

    env.update(settings)
    env.update(benchmark)
    env.update({"OUTPUT": output_directory})

    run_raw_command(command, env)


def run_fio(settings, benchmark):
    output_directory = supporting.generate_output_directory(settings, benchmark)
    output_file = f"{output_directory}/{benchmark['mode']}-{benchmark['iodepth']}-{benchmark['numjobs']}.json"

    command = [
        settings["fio_path"],
        "--output-format=json",
        f"--output={output_file}",
        settings["template"],
    ]

    command = supporting.expand_command_line(command, settings, benchmark)

    target_parameter = checks.check_target_type(benchmark["target"], settings["type"], benchmark["engine"])
    if target_parameter:
        command.append(f"{target_parameter}={benchmark['target']}")

    if not settings["dry_run"]:
        supporting.make_directory(output_directory)
        logger.info(f"Running [{' '.join(command)}]")
        run_command(settings, benchmark, command)
    # else:
    #    pprint.pprint(command)


def run_precondition_benchmark(settings, device, run):

    if settings["precondition"] and settings["type"] == "device":

        settings_copy = copy.deepcopy(settings)
        settings_copy["template"] = settings["precondition_template"]

        template = supporting.import_fio_template(settings["precondition_template"])

        benchmark = {
            "target": device,
            "mode": template["precondition"]["rw"],
            "iodepth": template["precondition"]["iodepth"],
            "block_size": template["precondition"]["bs"],
            "numjobs": template["precondition"]["numjobs"],
            "run": run,
        }
        run_fio(settings, benchmark)


def run_benchmarks(settings, benchmarks):
    # pprint.pprint(benchmarks)
    if not settings["quiet"]:
        run = 1
        for benchmark in ProgressBar(benchmarks):
            if settings["precondition_repeat"]:
                run_precondition_benchmark(settings, benchmark["target"], run)
                run += 1
            drop_caches(settings)
            run_fio(settings, benchmark)
    else:
        for benchmark in benchmarks:
            drop_caches(settings)
            run_fio(settings, benchmark)


def ProgressBar(iterObj):
    """https://stackoverflow.com/questions/3160699/python-progress-bar/49234284#49234284"""

    def SecToStr(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    L = len(iterObj)
    steps = {
        int(x): y
        for x, y in zip(
            linspace(0, L, min(100, L), endpoint=False),
            linspace(0, 100, min(100, L), endpoint=False),
        )
    }
    # quarter and half block chars
    qSteps = ["", "\u258E", "\u258C", "\u258A"]
    startT = time.time()
    timeStr = "   [0:00:00, -:--:--]"
    activity = [" -", " \\", " |", " /"]
    for nn, item in enumerate(iterObj):
        if nn in steps:
            done = "\u2588" * int(steps[nn] / 4.0) + qSteps[int(steps[nn] % 4)]
            todo = " " * (25 - len(done))
            barStr = "%4d%% |%s%s|" % (steps[nn], done, todo)
        if nn > 0:
            endT = time.time()
            timeStr = " [%s, %s]" % (
                SecToStr(endT - startT),
                SecToStr((endT - startT) * (L / float(nn) - 1)),
            )
        sys.stdout.write("\r" + barStr + activity[nn % 4] + timeStr)
        sys.stdout.flush()
        yield item
    barStr = "%4d%% |%s|" % (100, "\u2588" * 25)
    timeStr = "   [%s, 0:00:00]\n" % (SecToStr(time.time() - startT))
    sys.stdout.write("\r" + barStr + timeStr)
    sys.stdout.flush()
