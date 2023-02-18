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
    read_mean = [26.66, 8.84, 6.41, 11.41]
    read_err = [2.86, 3.38, 2.48, 1.69]
    x = np.arange(4)

    write_mean = [48.22, 26.95, 11.48, 9.79]
    write_err = [4.43, 5.03, 2.76, 1.38]

    width = 0.3

    # plot:
    fig, ax = plt.subplots()

    # plt.rcParams.update({
    #     "text.usetex": True,
    #     "font.family": "lmodern",
    #     # "font.sans-serif": "Helvetica"
    # })

    plt.yticks(fontsize=20)
    plt.xticks(x, ["fio end-to-end", "fio to\nnvme driver", "nvme driver\nto bdev", "bdev to\nhardware"])
    plt.xticks(rotation=45, ha='right', rotation_mode='anchor', fontsize=18)
    # plt.ylim(bottom=0, top=35)
    plt.ylabel("Time spent at layer (μs)", fontsize=20)
    ax.bar(x=x-0.2, height=read_mean, yerr=read_err, capsize=5, width=width, color=['grey', '#b6d7a8ff', '#f9cb9cff', '#9fc5e8ff'])
    ax.bar(x=x+0.2, height=write_mean, yerr=write_err, width=width, capsize=5, hatch="//", linewidth=2, facecolor="none", edgecolor=['grey', '#b6d7a8ff', '#f9cb9cff', '#9fc5e8ff'])
    plt.rcParams['hatch.linewidth'] = 2
    plt.tight_layout()
    plt.legend(["Reads", "Writes"], fontsize=16)

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
