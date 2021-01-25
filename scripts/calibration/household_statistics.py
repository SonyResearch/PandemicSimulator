"""This script plots the household family distribution in homes. This script should help tune
pandemic_simulator.environment.make_population.make_population method of the simulator.

The overview of home assignment to be followed is as follows:

a) "Only 4.5 percent of older adults live in nursing homes and
2 percent in assisted living facilities. The majority of older adults (93.5 percent) live in the community."
- https://www.ncbi.nlm.nih.gov/books/NBK51841/

b) "In 2019, there was an average of 1.93 children under 18 per family in the United States"
- https://www.statista.com/statistics/718084/average-number-of-own-children-per-family/

c) Assign at least one adult to each minor-included homes

Note: There are unittests that check the household distribution under test/environment/test_households.py
"""

import numpy as np

import pandemic_simulator as ps
from matplotlib import pyplot as plt, transforms


def plot_household_distribution():
    ps.init_globals()
    config = ps.sh.small_town_config
    cr = ps.env.globals.registry

    ps.env.make_locations(config)
    ps.env.make_population(config)

    retiree_homes = []
    minor_homes = []
    adult_homes = []

    homes = cr.location_ids_of_type(ps.env.Home)

    tot_persons = 0
    for home in homes:
        household = cr.get_persons_in_location(home)

        adults = 0
        minors = 0
        retirees = 0
        for member in household:
            if member.age <= 18:
                minors += 1
            elif 18 < member.age <= 65:
                adults += 1
            else:
                retirees += 1
        if minors > 0:
            minor_homes.append([minors, adults, retirees])
        elif adults > 0:
            adult_homes.append([minors, adults, retirees])
        elif retirees > 0:
            retiree_homes.append([minors, adults, retirees])
        tot_persons += len(household)

    minor_homes = np.asarray(minor_homes)
    adult_homes = np.asarray(adult_homes)
    retiree_homes = np.asarray(retiree_homes)

    n_rows = 2
    n_cols = 4
    plt.figure(figsize=(3 * n_cols, 3 * n_rows))
    plt_i = 0

    x = np.arange(3)
    colors = ['g', 'r', 'b']
    ylims = [0, max(np.max(minor_homes.sum(axis=0)), np.max(adult_homes.sum(axis=0)),
                    np.max(retiree_homes.sum(axis=0))) * 1.2]

    def plot_percent(n_homes: np.ndarray):
        for i, n in enumerate(n_homes):
            if n > 0:
                plt.text(i, n + 5, f'{n / config.num_persons * 100: 0.2f}%', ha="center", color=colors[i])

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.bar(x, minor_homes.sum(axis=0), color=colors, alpha=0.5, width=0.3)
    # plot_percent(minor_homes.sum(axis=0))
    plt.xticks(x, ['minors', 'adults', 'retirees'], fontsize=8)
    plt.title(f'{len(minor_homes)} Homes with minors')
    plt.ylim(ylims)

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.bar(x, adult_homes.sum(axis=0), color=colors, alpha=0.5, width=0.3)
    # plot_percent(adult_homes.sum(axis=0))
    plt.xticks(x, ['minors', 'adults', 'retirees'], fontsize=8)
    plt.title(f'{len(adult_homes)} Homes with young adults\n(no minors)')
    plt.ylim(ylims)

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.bar(x, retiree_homes.sum(axis=0), color=colors, alpha=0.5, width=0.3)
    # plot_percent(retiree_homes.sum(axis=0))
    plt.xticks(x, ['minors', 'adults', 'retirees'], fontsize=8)
    plt.title(f'{len(retiree_homes)} Homes with only retirees')
    plt.ylim(ylims)

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.hist(minor_homes[:, 0], [0, 1, 2, 3, 4], alpha=0.5, facecolor=colors[0], align='left', rwidth=0.3)
    plt.title(f'minor-occupancy (minor homes) \n(avg minors/home: {minor_homes[:, 0].mean(): 0.2f})')
    plt.ylabel('num homes')
    plt.xlabel('minors')

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.hist(minor_homes[:, 1], list(range(7)), alpha=0.5, facecolor=colors[1], align='left', rwidth=0.3)
    plt.title(f'adult-occupancy (minor homes) \n(avg adults/home: {minor_homes[:, 1].mean(): 0.2f})')
    plt.ylabel('num homes')
    plt.xlabel('adults')

    plt_i += 1
    plt.subplot(n_rows, n_cols, plt_i)
    plt.hist(minor_homes[:, 2], list(range(7)), alpha=0.5, facecolor=colors[2], align='left', rwidth=0.3)
    plt.title(f'retiree-occupancy (minor homes) \n(avg adults/home: {minor_homes[:, 2].mean(): 0.2f})')
    plt.ylabel('num homes')
    plt.xlabel('retirees')


    # plt.plot(minor_homes[:, 1])
    # plt.hist(minor_homes[:, 1], alpha=0.5)
    # plt.title('adults in minor homes')

    for home in minor_homes:
        assert home[1] > 0

    plt.tight_layout()
    plt.show()

    # plt.axvline(x=m, color="red")
    # trans = transforms.blended_transform_factory(ax.get_yticklabels()[0].get_transform(), ax.transData)
    # plt.text(0, m, f'{m: 0.2f}', color="red", ha="right", va="center", transform=trans)

    # plt.title(f'Location Assignee Visits\n(in {len(self._loc_assignee_visits)} days)')
    # plt.ylabel('num_visits / num_persons')
    # plt.ylim([0, None])
    # plt.legend(p, self._person_types[::-1])

    # assert len(minor_homes)
    # assert len(adult_homes)
    # assert len(retiree_homes)
    # assert tot_persons == config.num_persons
    #
    # # there should be non-zero homes with 1, 2, and 3 children
    # for i in range(1, 4):
    #     assert len(minor_homes[minor_homes[:, 0] == i]) > 0
    #
    #     # each minor home must contain an adult
    # for home in minor_homes:
    #     assert home[1] > 0
    #
    # # minor homes in general must also have retirees for small town config
    # assert np.sum(minor_homes, axis=0)[2] > 0
    #
    # # there should be non-zeros homes with 1 and >1 adults
    # assert len(adult_homes[adult_homes[:, 1] == 1]) > 0
    # assert len(adult_homes[adult_homes[:, 1] > 1]) > 0
    #
    # # no minors in adult homes
    # assert np.sum(adult_homes, axis=0)[0] == 0
    #
    # # adult homes in general must also have retirees for small town config
    # assert np.sum(adult_homes, axis=0)[2] > 0
    #
    # # there should be non-zeros with only retirees and no adults and minors
    # assert np.sum(retiree_homes, axis=0)[2] > 0
    # assert np.sum(retiree_homes, axis=0)[1] == 0
    # assert np.sum(retiree_homes, axis=0)[0] == 0
    #


if __name__ == '__main__':
    plot_household_distribution()
