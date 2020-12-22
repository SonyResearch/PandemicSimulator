# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from tqdm import trange

import pandemic_simulator as ps


def simple_worker_loop() -> None:
    """A simple worker loop tutorial, where a person goes to the assigned office during work time and goes back home
    after work."""
    print('\nSimple worker loop tutorial', flush=True)

    # The first thing to do at the start of each experiment is to initialize global parameters.
    # These parameters like numpy_rng, registry, etc. are shared across the entire repo.
    ps.init_globals(
        # init_globals also takes arguments like setting the random seed, or passing an existing instance of a registry
        seed=None,  # if None, a specific seed is not set and each experiment would initialized differently
        registry=None,  # if None, a registry is created and used
    )

    # Init locations
    home = ps.env.Home()
    work = ps.env.Office()  # any subclass of BusinessLocation can be a workplace, e.g. Bar, Restaurant, Hospital, etc.

    # Init a worker
    person = ps.env.Worker(
        person_id=ps.env.PersonID('worker', age=35),  # person_id is a unique id of this person
        home=home.id,  # specify the home_id that person is assigned to
        work=work.id,  # specify the id of the person's workplace
        work_time=work.state.open_time  # set work time of the person to office open hours
    )

    # Init simulator
    sim = ps.env.PandemicSim(
        locations=[work, home],  # a list of all locations
        persons=[person]  # a list of all persons
    )
    # PandemicSim by default creates and uses an SEIR infection model

    # Iterate through steps in the simulator, where each step advances an hour
    for _ in trange(24, desc='Simulating hour'):
        sim.step()

    # Or iterate by advancing in days by calling step_day in the simulator
    for _ in trange(10, desc='Simulating day'):
        sim.step_day()

    # The above loop iterates the simulator with no movement restrictions
    # To impose restrictions, for example, Stage-2 of austin_regulations
    sim.impose_regulation(ps.sh.austin_regulations[2])

    # Calling step_day now will run the simulator under Stage-2 regulation
    for _ in trange(10, desc='Simulating day (Under Stage-2)'):
        sim.step_day()


def simple_worker_loop_with_routines() -> None:
    """A simple worker loop tutorial with extra routines to other locations."""
    print('\nSimple worker loop with routines tutorial', flush=True)

    # The first thing to do at the start of each experiment is to initialize global parameters.
    # These parameters like numpy_rng, registry, etc. are shared across the entire repo.
    ps.init_globals(
        # init_globals also takes arguments like setting the random seed, or passing an existing instance of a registry
        seed=None,  # if None, a specific seed is not set and each experiment would initialized differently
        registry=None,  # if None, a registry is created and used
    )

    # Init locations
    home = ps.env.Home()
    work = ps.env.Office()  # any subclass of BusinessLocation can be a workplace, e.g. Bar, Restaurant, Hospital, etc.
    restaurant = ps.env.Restaurant()
    store = ps.env.GroceryStore()

    # Setup person routines
    # Routines are simple abstractions that define when, where and how-often a person should transition
    # between locations. The abstraction is specified using a PersonRoutine dataclass.
    # Here we'll show an example of a during-work routine to visit a restaurant for lunch.
    during_work_routines = [
        ps.env.PersonRoutine(
            start_loc=work.id,
            # the location where this routine can start. Here, we specify it to be the person's workplace id

            end_loc=restaurant.id,
            # the location where the person needs to go. Here, we specify it to be the restaurant

            valid_time=ps.env.SimTimeTuple(hours=tuple(range(11, 14)), week_days=tuple(range(0, 5))),
            # the time when this routine is due to be executed. Here, we specify it around Noon during weekdays
        )
    ]
    # more routines can be added to the list and the routines will be executed (if and when due) in the order of
    # the list.

    # Similarly, let's add an outside-work routine to visit a grocery store once every week
    outside_work_routines = [
        ps.env.PersonRoutine(
            start_loc=None,  # we specify it as None, so a person can go to the store directly after work if due

            end_loc=store.id,  # store id

            start_trigger_time=ps.env.SimTimeInterval(day=7),
            # notice that we set here start_trigger_time argument instead of valid_time. start_trigger_time specifies
            # the interval that triggers the start of the routine. In this case, the routine is triggered every third
            # seventh day. Once triggered it is queued to be executed.
        )

    ]

    # Init a worker
    person = ps.env.Worker(
        person_id=ps.env.PersonID('worker', age=35),  # person_id is a unique id of this person
        home=home.id,  # specify the home_id that person is assigned to
        work=work.id,  # specify the id of the person's workplace
        work_time=work.state.open_time,  # set work time of the person to office open hours
        during_work_routines=during_work_routines,
        outside_work_routines=outside_work_routines
    )

    # Init simulator
    sim = ps.env.PandemicSim(
        locations=[work, home, restaurant, store],  # a list of all locations
        persons=[person]  # a list of all persons
    )
    # PandemicSim by default creates and uses an SEIR infection model

    # Iterate by advancing in days by calling step_day in the simulator
    for _ in trange(10, desc='Simulating day'):
        sim.step_day()


if __name__ == '__main__':
    simple_worker_loop()
    simple_worker_loop_with_routines()
