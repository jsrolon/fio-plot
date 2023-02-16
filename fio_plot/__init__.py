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

def main():
    # y = [26.66, 17.82, 11.41]
    y = [26.66, 8.84, 6.41, 11.41]
    x = range(0, len(y))
    yerr = [2.86, 3.38, 2.48, 1.69]

    # plot:
    fig, ax = plt.subplots()

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "lmodern",
        # "font.sans-serif": "Helvetica"
    })

    plt.xticks(x, ["fio end-to-end", "fio to nvme driver", "nvme driver to bdev", "bdev to hardware"])
    plt.xticks(rotation=45, ha='right')
    # plt.ylim(bottom=0, top=35)
    plt.ylabel("Time spent at layer (μs)")
    ax.bar(x=x, height=y, yerr=yerr, capsize=5, color=['grey', '#b6d7a8ff', '#f9cb9cff', '#9fc5e8ff'])
    plt.tight_layout()
    plt.savefig("read.pdf", format='pdf')
    plt.show()

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
