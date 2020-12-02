# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from matplotlib import pyplot as plt

from pandemic_simulator.data import H5DataSaver, StageSchedule
from pandemic_simulator.environment import PandemicSimOpts, italian_regulations, swedish_regulations
from pandemic_simulator.script_helpers import EvaluationOpts, experiment_main, make_evaluation_plots


def eval_government_strategies(experiment_name: str, opts: EvaluationOpts) -> None:
    data_saver = H5DataSaver(experiment_name, path=opts.data_saver_path)
    print('Running Swedish strategy')
    experiment_main(sim_opts=PandemicSimOpts(),
                    sim_non_cli_opts=opts.default_sim_non_cli_opts,
                    data_saver=data_saver,
                    pandemic_regulations=swedish_regulations,
                    stages_to_execute=swedish_strategy,
                    num_random_seeds=opts.num_seeds,
                    max_episode_length=opts.max_episode_length,
                    exp_id=0)

    print('Running Italian strategy')
    experiment_main(sim_opts=PandemicSimOpts(),
                    sim_non_cli_opts=opts.default_sim_non_cli_opts,
                    data_saver=data_saver,
                    pandemic_regulations=italian_regulations,
                    stages_to_execute=italian_strategy,
                    num_random_seeds=opts.num_seeds,
                    max_episode_length=opts.max_episode_length,
                    exp_id=1)


if __name__ == '__main__':
    swedish_strategy = [StageSchedule(stage=0, end_day=3),
                        StageSchedule(stage=1, end_day=None)]
    italian_strategy = [StageSchedule(stage=0, end_day=3),
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

    exp_name = 'swedish_italian_strategies'
    try:
        eval_government_strategies(exp_name, opts)
    except ValueError:
        # Expect a value error because we are reusing the same directory.
        pass
    make_evaluation_plots(exp_name=exp_name, data_saver_path=opts.data_saver_path, param_labels=['SWE', 'ITA'],
                          bar_plot_xlabel='Real Government Strategies',
                          annotate_stages=True,
                          show_cumulative_reward=False,
                          show_time_to_peak=False, show_pandemic_duration=True,
                          )
    plt.show()
