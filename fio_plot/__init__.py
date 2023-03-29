# Generates graphs from FIO output data for various IO queue depthts
#
# Output in PNG format.
#
# Requires matplotib and numpy.
#
# import pprint
import matplotlib.pyplot as plt
from .fiolib import (
    argparsing,
    flightchecks as checks,
    getdata
)
import numpy as np

def main():
    # y = [26.66, 17.82, 11.41]
    # read_mean = [26.66, 8.84, 6.41, 11.41]
    # read_err = [2.86, 3.38, 2.48, 1.69]
    read_mean = [8.84, 6.41, 11.41]
    read_err = [3.38, 2.48, 1.69]

    read_means = [[8.84], [6.41], [11.41]]
    read_errs = [[3.38], [2.48], [1.69]]

    x_first = np.arange(1)
    x = np.arange(2, 4)

    # write_mean = [48.22, 26.95, 11.48, 9.79]
    # write_err = [4.43, 5.03, 2.76, 1.38]
    write_mean = [26.95, 11.48, 9.79]
    write_err = [5.03, 2.76, 1.38]

    width = 0.3

    # plot:
    fig, ax = plt.subplots()

    # plt.rcParams.update({
    #     "text.usetex": True,
    #     "font.family": "lmodern",
    #     # "font.sans-serif": "Helvetica"
    # })

    plt.yticks(fontsize=16)
    # plt.xticks(x, ["fio end\nto end", "fio to nvme\ndriver", "nvme driver\nto bdev", "bdev to\nhardware"])
    plt.xticks(x_first, ["fio end\nto end"])
    plt.xticks(fontsize=14)
    # plt.ylim(bottom=0, top=35)
    plt.ylabel("Time (μs)", fontsize=16)

    # first bar, stacked reads
    f_read = ax.bar(x=x_first-0.2, height=read_means[0], yerr=read_errs[0], capsize=5, width=width, color=['#b6d7a8ff'])
    ax.bar(x=x_first-0.2, height=read_means[1], yerr=read_errs[1], capsize=5, width=width, color=['#f9cb9cff'], bottom=read_means[0])
    ax.bar(x=x_first-0.2, height=read_means[2], yerr=read_errs[2], capsize=5, width=width, color=['#9fc5e8ff'], bottom=15.25)

    # first bar, stacked writes
    f_write = ax.bar(x=x_first+0.2, height=write_mean[0], yerr=write_err[0], capsize=5, hatch="//", linewidth=2, facecolor="none", width=width, edgecolor=['#b6d7a8ff'])
    ax.bar(x=x_first+0.2, height=write_mean[1], yerr=write_err[1], capsize=5, hatch="//", linewidth=2, facecolor="none", width=width, edgecolor=['#f9cb9cff'],
           bottom=write_mean[0])
    ax.bar(x=x_first+0.2, height=write_mean[2], yerr=write_err[2], capsize=5, hatch="//", linewidth=2, facecolor="none", width=width, edgecolor=['#9fc5e8ff'],
           bottom=38.43)

    # ax.bar(x=x-0.2, height=read_mean, yerr=read_err, capsize=5, width=width, color=['#b6d7a8ff', '#f9cb9cff', '#9fc5e8ff'])
    # ax.bar(x=x+0.2, height=write_mean, yerr=write_err, width=width, capsize=5, hatch="//", linewidth=2, facecolor="none", edgecolor=['#b6d7a8ff', '#f9cb9cff', '#9fc5e8ff'])
    plt.rcParams['hatch.linewidth'] = 2
    plt.legend(handles=[f_read, f_write], labels=["Reads", "Writes"], fontsize=16)

    fig = plt.gcf()
    size = fig.set_size_inches(6.4, 3)
    plt.tight_layout()

    ax.set_frame_on(False)

    plt.savefig("readwrite.pdf", format='pdf')
    # plt.show()

    # settings = {}
    # option_found = False
    # parser = argparsing.set_arguments()
    # settings = vars(argparsing.get_command_line_arguments(parser))
    # checks.run_preflight_checks(settings)
    # routing_dict = getdata.get_routing_dict()
    #
    # for item in routing_dict.keys():
    #     if settings[item]:
    #         settings = getdata.configure_default_settings(settings, routing_dict, item)
    #         # print(settings)
    #         data = routing_dict[item]["get_data"](settings)
    #         routing_dict[item]["function"](settings, data)
    #         option_found = True
    #
    # checks.post_flight_check(parser, option_found)
