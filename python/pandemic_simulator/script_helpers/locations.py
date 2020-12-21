# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import List, Sequence

from ..environment import Location, LocationConfig

__all__ = ['make_locations']


def make_locations(location_configs: Sequence[LocationConfig]) -> List[Location]:
    """Returns a list of location instances from all_location_opts"""
    return [config.location_type(loc_id=f'{config.location_type.__name__}_{i}',
                                 init_state=config.location_type.state_type(**config.state_opts))
            for config in location_configs for i in range(config.num)]
