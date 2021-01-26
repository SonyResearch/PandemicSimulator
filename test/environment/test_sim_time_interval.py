# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from pandemic_simulator.environment import SimTime, SimTimeInterval


def test_sim_time_interval_trigger_hour() -> None:
    hour = 5
    interval = SimTimeInterval(hour=hour)
    for i in range(1, 3):
        assert interval.trigger_at_interval(SimTime(hour=hour * i))
        assert not interval.trigger_at_interval(SimTime(hour=hour * i + 1))
        assert not interval.trigger_at_interval(SimTime(hour=hour * i - 1))


def test_sim_time_interval_trigger_day() -> None:
    day = 5
    hour = 6
    interval = SimTimeInterval(day=day, hour=hour)
    for i in range(1, 3):
        assert interval.trigger_at_interval(SimTime(day=day * i, hour=hour * i))
        assert not interval.trigger_at_interval(SimTime(day=day * i + 1))
        assert not interval.trigger_at_interval(SimTime(day=day * i - 1))
        assert not interval.trigger_at_interval(SimTime(day=day, hour=1))


def test_sim_time_interval_trigger_offset() -> None:
    offset_hour = 2
    offset_day = 1
    hour = 1
    day = 3

    interval = SimTimeInterval(hour=hour, day=day, offset_hour=offset_hour, offset_day=offset_day)
    for i in range(1, 3):
        assert interval.trigger_at_interval(SimTime(day=day * i + offset_day, hour=hour * i + offset_hour))
        assert not interval.trigger_at_interval(SimTime(day=day * i, hour=hour * i))
        assert not interval.trigger_at_interval(SimTime(day=day * i + 1))
        assert not interval.trigger_at_interval(SimTime(day=day * i - 1))
        assert not interval.trigger_at_interval(SimTime(day=day, hour=1))
