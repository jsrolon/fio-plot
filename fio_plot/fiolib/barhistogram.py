#!/usr/bin/env python3
import numpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
from pathlib import Path
import re
import seaborn as sns

# import pprint
from . import (
    shared_chart as shared,
    supporting
)

def sort_latency_keys(latency):
    """The FIO latency data has latency buckets and those are sorted ascending.
    The milisecond data has a >=2000 bucket which cannot be sorted in a 'normal'
    way, so it is just stuck on top. This function resturns a list of sorted keys.
    """
    placeholder = ""
    tmp = []
    for item in latency:
        if item == ">=2000":
            placeholder = ">=2000"
        else:
            tmp.append(item)

    tmp.sort(key=int)
    if placeholder:
        tmp.append(placeholder)
    return tmp


def sort_latency_data(latency_dict):
    """The sorted keys from the sort_latency_keys function are used to create
    a sorted list of values, matching the order of the keys."""
    keys = latency_dict.keys()
    values = {"keys": None, "values": []}
    sorted_keys = sort_latency_keys(keys)
    values["keys"] = sorted_keys
    for key in sorted_keys:
        values["values"].append(latency_dict[key])
    return values


def autolabel(rects, axis):
    """This function puts a value label on top of a 2d bar. If a bar is so small
    it's barely visible, if at all, the label is omitted."""
    fontsize = 6
    for rect in rects:
        height = rect.get_height()
        if height >= 1:
            axis.text(
                rect.get_x() + rect.get_width() / 2.0,
                1 + height,
                "{}%".format(int(height)),
                ha="center",
                fontsize=fontsize,
            )
        elif height > 0.4:
            axis.text(
                rect.get_x() + rect.get_width() / 2.0,
                1 + height,
                "{:3.2f}%".format(height),
                ha="center",
                fontsize=fontsize,
            )


def chart_latency_histogram(settings, dataset):
    """This function is responsible to draw the 2D latency histogram,
    (a bar chart)."""
    rawdata = dataset[0]["rawdata"][0]
    job_options = rawdata["jobs"][0]["job options"]

    for numjob in settings["numjobs"]:
        fig, hist_axes = plt.subplots()
        # hist_axes.set_xscale('log')
        hist_axes.set_yscale('symlog', linthresh=1e-7)
        hist_axes.grid(ls='--', lw=0.25)
        # hist_axes.set_frame_on(False)
        hist_axes.set_ylabel("Density (log)")
        hist_axes.set_xlabel("Latency (ms)")

        x = []
        for iodepth in settings["iodepth"]:
            data = []
            for file in glob.glob(settings["input_directory"][0] + f'/{settings["rw"]}-iodepth-{iodepth}-numjobs-{numjob}_lat*.log'):
                file_data = numpy.genfromtxt(file, delimiter=',', usecols=[1], dtype=[('latency', float)])
                data.extend(file_data["latency"])

            dist_axes = sns.distplot(data, hist=False, rug=True, norm_hist=False, label=iodepth, kde_kws={"fill": True, "bw_adjust": 3})
            # dist_axes.set_xscale('log')

            # hist_axes.set_title(f"iodepth={iodepth}", fontdict={"fontsize": 6})
            # hist_axs[i][j].set_xlim(xmin=0)
            # hist_axs[i][j].set_xscale('log')
            # hist_axs[i][j].hist(data, density=True)

        hist_axes.set_title(" | ".join(
            [rawdata['fio version'],
             "spdk v22.01",
             f"rw {settings['rw']}",
             f"ioengine {job_options['ioengine']}",
             f"bs {job_options['bs']}"]),
            fontdict={"fontsize": 9})

        # hist_axes.set_xticks([1e4, 5e4, 1e5, 1e6], labels=["10ms", "50ms", "100ms", "1s"])
        hist_axes.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, pos: '{:.0f}'.format(x / 1e3)))

        handles, labels = hist_axes.get_legend_handles_labels()
        handles, labels = zip(*sorted(list(zip(handles, labels)), key=lambda item: int(item[1])))
        hist_axes.legend(handles, labels, title="Queue depth")

        run_results_folder = Path(settings['input_directory'][0]).parts[-4]
        run_name = re.sub(r'-2022.+$', '', run_results_folder)

        # hist_axes.set_ylim(ymax=1e-3)
        hist_axes.set_xlim(xmin=0)

        # Hide the right and top spines
        hist_axes.spines.right.set_visible(False)
        hist_axes.spines.top.set_visible(False)

        # Only show ticks on the left and bottom spines
        hist_axes.yaxis.set_ticks_position('left')
        hist_axes.xaxis.set_ticks_position('bottom')

        fig.suptitle(f"{run_name}, {numjob} thread(s)")
        # plt.tight_layout()
        supporting.save_png(settings, plt, fig)
