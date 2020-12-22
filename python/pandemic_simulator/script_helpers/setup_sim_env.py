# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional, List

from .covid_regulations import austin_regulations
from .locations import make_locations
from .population import make_population
from ..environment import SumReward, RewardFunctionFactory, RewardFunctionType, DoneFunction, \
    PandemicSim, PandemicGymEnv, SEIRModel, InfectionSummary, SpreadProbabilityParams, \
    RandomPandemicTesting, MaxSlotContactTracer, PandemicSimOpts, PandemicSimConfig, PandemicRegulation, globals, \
    JobCounselor

__all__ = ['make_sim', 'make_gym_env']


def make_sim(sim_config: PandemicSimConfig, sim_opts: PandemicSimOpts = PandemicSimOpts()) -> PandemicSim:
    """
    A helper that sets up pandemic_simulator simulator

    :param sim_config: Config for setting up the simulator
    :param sim_opts: Simulator options
    :return: PandemicSim instance
    """
    assert globals.registry, 'Environment globals are not initialized, call pandemic_simulator.init_globals() first.'

    # make locations
    locations = make_locations(sim_config.location_configs)

    # make population
    persons = make_population(num_persons=sim_config.num_persons,
                              job_counselor=JobCounselor(sim_config.location_configs),
                              regulation_compliance_prob=sim_opts.regulation_compliance_prob)

    # make infection model
    infection_model = SEIRModel(spread_probability_params=SpreadProbabilityParams(sim_opts.infection_spread_rate_mean,
                                                                                  sim_opts.infection_spread_rate_sigma))

    # setup pandemic testing
    pandemic_testing = RandomPandemicTesting(spontaneous_testing_rate=sim_opts.spontaneous_testing_rate,
                                             symp_testing_rate=sim_opts.symp_testing_rate,
                                             critical_testing_rate=sim_opts.critical_testing_rate,
                                             testing_false_positive_rate=sim_opts.testing_false_positive_rate,
                                             testing_false_negative_rate=sim_opts.testing_false_negative_rate,
                                             retest_rate=sim_opts.retest_rate)

    # create contact tracing app (optional)
    contact_tracer = MaxSlotContactTracer(
        storage_slots=sim_opts.contact_tracer_history_size) if sim_opts.use_contact_tracer else None

    # setup sim
    return PandemicSim(persons=persons,
                       locations=locations,
                       infection_model=infection_model,
                       pandemic_testing=pandemic_testing,
                       contact_tracer=contact_tracer,
                       infection_threshold=sim_opts.infection_threshold)


def make_gym_env(sim_config: PandemicSimConfig,
                 sim_opts: PandemicSimOpts = PandemicSimOpts(),
                 pandemic_regulations: Optional[List[PandemicRegulation]] = None,
                 done_fn: Optional[DoneFunction] = None) -> PandemicGymEnv:
    """
    A helper that sets up pandemic_simulator gym env

    :param sim_config: Config for setting up the simulator
    :param sim_opts: Simulator options
    :param pandemic_regulations: A list of pandemic regulations to use. If None, austin_regulations are used.
    :param done_fn: optional done fns for the env
    :return: PandemicGymEnv instance
    """
    # setup sim
    sim = make_sim(sim_config, sim_opts)

    # setup reward fn
    pandemic_regulations = pandemic_regulations if pandemic_regulations is not None else austin_regulations

    if sim_config.max_hospital_capacity == -1:
        raise Exception("Nothing much to optimise if max hospital capacity is -1.")

    reward_fn = SumReward(
        reward_fns=[
            RewardFunctionFactory.default(RewardFunctionType.INFECTION_SUMMARY_ABOVE_THRESHOLD,
                                          summary_type=InfectionSummary.CRITICAL,
                                          threshold=sim_config.max_hospital_capacity),
            RewardFunctionFactory.default(RewardFunctionType.INFECTION_SUMMARY_ABOVE_THRESHOLD,
                                          summary_type=InfectionSummary.CRITICAL,
                                          threshold=3 * sim_config.max_hospital_capacity),
            RewardFunctionFactory.default(RewardFunctionType.LOWER_STAGE,
                                          num_stages=len(pandemic_regulations)),
            RewardFunctionFactory.default(RewardFunctionType.SMOOTH_STAGE_CHANGES,
                                          num_stages=len(pandemic_regulations))
        ],
        weights=[.4, 1, .1, 0.02]
    )

    # setup env
    return PandemicGymEnv(pandemic_sim=sim,
                          stage_to_regulation={reg.stage: reg for reg in pandemic_regulations},
                          sim_steps_per_regulation=sim_opts.sim_steps_per_regulation,
                          reward_fn=reward_fn,
                          done_fn=done_fn)
