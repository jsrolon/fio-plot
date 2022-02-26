#!/usr/bin/env python3
import logging
import os
import sys
import shutil

logger = logging.getLogger(__name__)


def get_default_settings():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    settings = {}
    settings["target"] = []
    settings["template"] = os.path.join(dir_path, "..", "templates", "fio-job-template.fio")
    settings["engine"] = ["libaio"]
    settings["mode"] = ["randread", "randwrite"]
    settings["iodepth"] = [1, 2, 4, 8, 16, 32, 64]
    settings["numjobs"] = [1, 2, 4, 8, 16, 32, 64]
    settings["block_size"] = ["4k"]
    settings["direct"] = 1
    settings["size"] = None
    settings["precondition"] = False
    settings["precondition_template"] = "precondition.fio"
    settings["precondition_repeat"] = False
    settings["entire_device"] = False
    settings["ss"] = False
    settings["ss_dur"] = None
    settings["ss_ramp"] = None
    settings["rwmixread"] = None
    settings["runtime"] = 60
    settings["loops"] = 1
    settings["time_based"] = False
    settings["extra_opts"] = []
    settings["loginterval"] = 500
    settings["mixed"] = ["readwrite", "rw", "randrw"]
    settings["invalidate"] = 1
    settings["ceph_pool"] = None
    settings["fio_path"] = "fio"
    settings["loop_items"] = [
        "target",
        "engine",
        "mode",
        "iodepth",
        "numjobs",
        "block_size",
    ]
    settings["filter_items"] = [
        "filter_items",
        "loop_items",
        "dry_run",
        "mixed",
        "quiet",
    ]
    return settings


def check_settings(settings):
    if shutil.which(settings["fio_path"]) is None:
        if os.path.exists(settings["fio_path"]):
            if not os.access(settings["fio_path"], os.X_OK):
                logger.error(f"Fio binary at {settings['fio_path']} is not executable. Check its file permissions.")
                sys.exit(1)
        else:
            logger.error(f"Fio executable at {settings['fio_path']} not found. Is Fio installed?")
            sys.exit(1)

    """Some basic error handling."""
    if not os.path.exists(settings["template"]):
        logger.error(f"The specified template {settings['template']} does not exist.")
        sys.exit(6)

    if settings["type"] not in ["device", "rbd"] and not settings["size"]:
        logger.error("When the target is a file or directory, --size must be specified.")
        sys.exit(4)

    if settings["type"] == "directory":
        for item in settings["target"]:
            if not os.path.exists(item):
                logger.error(f"\nThe target directory ({item}) doesn't seem to exist.\n")
                sys.exit(5)

    if settings["type"] == "rbd":
        if not settings["ceph_pool"]:
            logger.error(
                "\nCeph pool (--ceph-pool) must be specified when target type is rbd.\n"
            )
            sys.exit(6)

    if settings["type"] == "rbd" and settings["ceph_pool"]:
        if settings["template"] == "./fio-job-template.fio":
            logger.error(
                "Please specify the appropriate Fio template (--template).\n\
                    The example fio-job-template-ceph.fio can be used."
            )
            sys.exit(7)

    if "spdk" in settings["engine"]:
        if len(settings["engine"]) != 1:
            logger.error("SPDK requires exclusive access to the NVMe device, cannot be used with other engines")
            sys.exit(9)

        if settings["type"] != "file":
            logger.error("SPDK fio plugin requires --type=file")
            sys.exit(9)

        if not ("trtype=" in target for target in settings["target"]):
            logger.error("SPDK fio plugin requires target filename to be an SPDK Transport Identifier string")
            sys.exit(9)

        if not settings["env_vars"] or not ("LD_PRELOAD" in env_var for env_var in settings["env_vars"]):
            logger.error("SPDK fio plugin requires LD_PRELOAD env variable to point to compiled SPDK. Use --env-vars")
            sys.exit(9)

    for mode in settings["mode"]:
        if mode in settings["mixed"]:
            if settings["rwmixread"]:
                settings["loop_items"].append("rwmixread")
            else:
                logger.error(
                    "\nIf a mixed (read/write) mode is specified, please specify --rwmixread\n"
                )
                sys.exit(8)
        else:
            settings["filter_items"].append("rwmixread")
