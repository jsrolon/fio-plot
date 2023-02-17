#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import palettable
from pathlib import Path
import re

from . import (
    supporting,
    shared_chart as shared,
    tables
)


def calculate_font_size(settings, x_axis):
    max_label_width = max(tables.get_max_width([x_axis], len(x_axis)))
    fontsize = 0
    #
    # This hard-coded font sizing is ugly but if somebody knows a better algorithm...
    #
    if settings["group_bars"]:
        if max_label_width > 10:
            fontsize = 6
        elif max_label_width > 15:
            fontsize = 5
        else:
            fontsize = 8
    else:
        if max_label_width > 18:
            fontsize = 5
        else:
            fontsize = 8
    return fontsize


def create_bars_and_xlabels(settings, data, iops_axes, lat_axes):

    return_data = {"ax1": None, "ax3": None, "rects1": None, "rects2": None}

    iops = data["y1_axis"]["data"]
    latency = np.array(data["y2_axis"]["data"], dtype=float)
    width = 0.9

    color_iops = "#a8ed63"
    color_lat = "#34bafa"

    if settings["group_bars"]:
        x_pos1 = np.arange(1, len(iops) + 1, 1)
        x_pos2 = np.arange(len(iops) + 1, len(iops) + len(latency) + 1, 1)

        rects1 = iops_axes.bar(x_pos1, iops, width, color=color_iops)
        # rects2 = lat_axes.bar(x_pos2, latency, width, color=color_lat)

        x_axis = data["x_axis"] * 2
        ltest = np.arange(1, len(x_axis) + 1, 1)

    else:
        x_pos = np.arange(0, (len(iops) * 2), 2)

        rects1 = iops_axes.bar(x_pos, iops, width, color=color_iops)
        rects2 = lat_axes.bar(x_pos + width, latency, width, color=color_lat)

        x_axis = data["x_axis"]
        ltest = np.arange(0.45, (len(iops) * 2), 2)

    iops_axes.set_ylabel(data["y1_axis"]["format"])
    lat_axes.set_ylabel(data["y2_axis"]["format"])
    iops_axes.set_xlabel(settings["label"])
    iops_axes.set_xticks(ltest)

    if settings["compare_graph"]:
        fontsize = calculate_font_size(settings, x_axis)
        iops_axes.set_xticklabels(labels=x_axis, fontsize=fontsize)
    # else:
        # ax1.set_xticklabels(labels=x_axis)

    return_data["rects1"] = rects1
    return_data["rects2"] = rects2
    return_data["ax1"] = iops_axes
    return_data["ax3"] = lat_axes

    return return_data


def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    #pprint.pprint(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)
    # pprint.pprint(data)
    fig, iops_axes = plt.subplots()
    # fig.set_size_inches(6.4, 6.4)

    iops_axes.set_ylabel("Mean IOPS", fontsize=20)
    iops_axes.set_xlabel("Threads", fontsize=20)

    # iops_axes.set_prop_cycle(marker=['o', '+', 'x'])
    # iops_axes.set_prop_cycle(color=palettable.scientific.sequential.Acton_6.mpl_colors)

    iodepths = {}
    for job in dataset[0]["rawdata"]:
        options = job["jobs"][0]["job options"]

        # iops_axes.set_title(" | ".join(
        #     [job['fio version'], "spdk v22.01", f"rw {options['rw']}", f"ioengine {options['ioengine']}", f"bs {options['bs']}"]),
        #                     fontdict={"fontsize": 9})

        job = job["jobs"][0]["read"] # todo: dinamically choose read/write
        iodepth = options["iodepth"]
        numjobs = options["numjobs"]

        if iodepth not in iodepths:
            iodepths[iodepth] = {}

        iodepths[iodepth][numjobs] = {
            "min": job["iops_min"],
            "max": job["iops_max"],
            "mean": job["iops_mean"],
            "stddev": job["iops_stddev"]
        }

    for iodepth, value in sorted(iodepths.items(), key=lambda item: int(item[0])):
        sorted_iodepth = sorted(value.items(), key=lambda item: int(item[0]))
        x = [tuple[0] for tuple in sorted_iodepth]
        y = [tuple[1]["mean"] for tuple in sorted_iodepth]
        yerr = [tuple[1]["stddev"] for tuple in sorted_iodepth]

        iops_axes.errorbar(x, y, yerr, fmt="o", linewidth=1, capsize=6, ls='-', label=iodepth, mec='black', mew=0.25, ms=15)
        # iops_axes.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        iops_axes.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x / 1000) + 'K'))

    handles, labels = iops_axes.get_legend_handles_labels()
    handles, labels = zip(*sorted(list(zip(handles, labels)), key=lambda item: int(item[1])))
    fig.legend(handles, labels, title="Queue depth", fontsize=20)
    # fig.tight_layout()
    # fig.subplots_adjust(bottom=0.25)

    iops_axes.set_ylim(ymin=0, ymax=8e5)
    iops_axes.grid(ls='--', lw=2.5, axis="y")
    iops_axes.set_frame_on(False)
    iops_axes.tick_params(axis='both', which='major', labelsize=20)

    run_results_folder = Path(settings['input_directory'][0]).parts[-4]
    run_name = re.sub(r'-2022.+$', '', run_results_folder)

    mid = (fig.subplotpars.right + fig.subplotpars.left) / 2
    fig.suptitle(run_name, x=mid, fontsize=20)
    # plt.show()

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)


def compchart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for creating bar charts that compare data."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set_improved(settings, dataset, dataset_types)
    
    # pprint.pprint(data)

    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    #
    # Puts in the credit source (often a name or url)
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax1)

    ax2.axis("off")

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)
    rects1 = return_data["rects1"]
    rects2 = return_data["rects2"]
    ax1 = return_data["ax1"]
    ax3 = return_data["ax3"]
    #
    # Set title
    settings["type"] = ""
    settings["iodepth"] = dataset_types["iodepth"]
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(settings, plt, skip_keys=["iodepth"])
    else:
        supporting.create_title_and_sub(settings, plt, skip_keys=[])

    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    shared.autolabel(rects2, ax3)

    tables.create_stddev_table(settings, data, ax2)

    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2)

    # Create legend
    ax2.legend(
        (rects1[0], rects2[0]),
        (data["y1_axis"]["format"], data["y2_axis"]["format"]),
        loc="center left",
        frameon=False,
    )

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
