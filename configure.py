from typing import NamedTuple


class StandingConfig(NamedTuple):
    name: str
    source_range: str
    destination_range: str


feeds = [
    StandingConfig(name='first_half_standings',
                   source_range='AX7:AX87',
                   destination_range='E96'),

    StandingConfig(name='second_half_standings',
                   source_range='CT7:CT87',
                   destination_range='H96'),

    StandingConfig(name='major_standings',
                   source_range='CV7:CV87',
                   destination_range='K96'),

    StandingConfig(name='total_standings',
                   source_range='C7:C87',
                   destination_range='Q96'),
]