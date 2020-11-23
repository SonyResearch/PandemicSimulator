# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from matplotlib import pyplot as plt

from pandemic_simulator.data import H5DataSaver, StageSchedule
from pandemic_simulator.environment import PandemicSimOpts, austin_regulations, PandemicSimNonCLIOpts
from pandemic_simulator.script_helpers import EvaluationOpts, experiment_main, make_evaluation_plots, \
    medium_town_population_params


def eval_government_strategies(experiment_name: str, opts: EvaluationOpts):
    data_saver = H5DataSaver(experiment_name, path=opts.data_saver_path)
    experiment_main(sim_opts=PandemicSimOpts(),
                    sim_non_cli_opts=PandemicSimNonCLIOpts(medium_town_population_params),
                    data_saver=data_saver,
                    pandemic_regulations=austin_regulations,
                    stages_to_execute=austin_strategy,
                    num_random_seeds=opts.num_seeds,
                    max_episode_length=opts.max_episode_length,
                    exp_id=1)


if __name__ == '__main__':
    austin_strategy = [StageSchedule(stage=0, end_day=3),
                       StageSchedule(stage=1, end_day=8),
                       StageSchedule(stage=2, end_day=13),
                       StageSchedule(stage=3, end_day=25),
                       StageSchedule(stage=4, end_day=59),
                       StageSchedule(stage=3, end_day=79),
                       StageSchedule(stage=2, end_day=None)]

    opts = EvaluationOpts(
        num_seeds=30,
        max_episode_length=180,
        enable_warm_up=False
    )

    exp_name = 'bar impact'
    try:
        eval_government_strategies(exp_name, opts)
    except ValueError:
        pass
    make_evaluation_plots(exp_name=exp_name, data_saver_path=opts.data_saver_path, param_labels=[' '],
                          bar_plot_xlabel='Bar Impact Strategy',
                          annotate_stages=True,
                          show_cumulative_reward=False,
                          show_time_to_peak=True, show_pandemic_duration=True,
                          )
    plt.show()
