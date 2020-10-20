# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional, List

import numpy as np

from .locations import make_standard_locations
from .population import make_us_age_population
from ..environment import SumReward, RewardFunctionFactory, RewardFunctionType, DoneFunction, \
    PandemicSim, PandemicGymEnv, CityRegistry, SEIRModel, Hospital, InfectionSummary, \
    SpreadProbabilityParams, RandomPandemicTesting, MaxSlotContactTracer, \
    PandemicSimOpts, PandemicSimNonCLIOpts, PandemicRegulation, austin_regulations

__all__ = ['make_sim', 'make_gym_env']


def make_sim(sim_opts: PandemicSimOpts,
             sim_non_cli_opts: PandemicSimNonCLIOpts,
             city_registry: Optional[CityRegistry] = None,
             numpy_rng: Optional[np.random.RandomState] = None) -> PandemicSim:
    """
    A helper that sets up pandemic_simulator simulator

    :param sim_opts: Simulator options (that can be potentially passed as command line args)
    :param sim_non_cli_opts: Simulator options that cannot be passed as command line args
    :param city_registry: optional city registry (if None, one is created and used)
    :param numpy_rng: rng
    :return: PandemicSim instance
    """

    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    # make a city registry
    cr = city_registry or CityRegistry()

    # make locations
    locations = make_standard_locations(population_params=sim_non_cli_opts.population_params,
                                        registry=cr,
                                        numpy_rng=numpy_rng)

    # make population
    persons = make_us_age_population(population_params=sim_non_cli_opts.population_params,
                                     regulation_compliance_prob=sim_opts.regulation_compliance_prob,
                                     registry=cr,
                                     numpy_rng=numpy_rng)

    # make infection model
    infection_model = SEIRModel(spread_probability_params=SpreadProbabilityParams(
        sim_opts.infection_spread_rate_mean,
        sim_opts.infection_spread_rate_sigma),
        numpy_rng=numpy_rng)

    # setup pandemic testing
    pandemic_testing = RandomPandemicTesting(spontaneous_testing_rate=sim_opts.spontaneous_testing_rate,
                                             symp_testing_rate=sim_opts.symp_testing_rate,
                                             critical_testing_rate=sim_opts.critical_testing_rate,
                                             testing_false_positive_rate=sim_opts.testing_false_positive_rate,
                                             testing_false_negative_rate=sim_opts.testing_false_negative_rate,
                                             retest_rate=sim_opts.retest_rate,
                                             numpy_rng=numpy_rng)

    # create contact tracing app (optionally)
    contact_tracer = (MaxSlotContactTracer(storage_slots=sim_opts.contact_tracer_history_size)
                      if sim_opts.use_contact_tracer else None)

    # setup sim
    return PandemicSim(persons=persons,
                       locations=locations,
                       infection_model=infection_model,
                       pandemic_testing=pandemic_testing,
                       registry=cr,
                       contact_tracer=contact_tracer,
                       infection_threshold=sim_opts.infection_threshold,
                       numpy_rng=numpy_rng)


def make_gym_env(sim_opts: PandemicSimOpts,
                 sim_non_cli_opts: PandemicSimNonCLIOpts,
                 pandemic_regulations: Optional[List[PandemicRegulation]] = None,
                 city_registry: Optional[CityRegistry] = None,
                 done_fn: Optional[DoneFunction] = None,
                 numpy_rng: Optional[np.random.RandomState] = None) -> PandemicGymEnv:
    """
    A helper that sets up pandemic_simulator gym env

    :param sim_opts: Simulator options (that can be potentially passed as command line args)
    :param sim_non_cli_opts: Simulator options that cannot be passed as command line args
    :param pandemic_regulations: A list of pandemic regulations to use. If None, austin_regulations are used.
    :param city_registry: optional city registry (if None, one is created and used)
    :param done_fn: optional done fns for the env
    :param numpy_rng: rng
    :return: PandemicGymEnv instance
    """
    # setup city registry
    cr = city_registry or CityRegistry()

    # setup sim
    sim = make_sim(sim_opts, sim_non_cli_opts, city_registry=cr, numpy_rng=numpy_rng)

    # setup reward fn
    pandemic_regulations = pandemic_regulations if pandemic_regulations is not None else austin_regulations
    hospital_params = sim_non_cli_opts.population_params.location_type_to_params[Hospital]
    max_hospitals_capacity = hospital_params.num * hospital_params.visitor_capacity
    done_threshold = 3 * max_hospitals_capacity
    reward_fn = SumReward(
        reward_fns=[
            RewardFunctionFactory.default(RewardFunctionType.INFECTION_SUMMARY_ABOVE_THRESHOLD,
                                          summary_type=InfectionSummary.CRITICAL,
                                          threshold=max_hospitals_capacity),
            RewardFunctionFactory.default(RewardFunctionType.INFECTION_SUMMARY_ABOVE_THRESHOLD,
                                          summary_type=InfectionSummary.CRITICAL,
                                          threshold=done_threshold),
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
