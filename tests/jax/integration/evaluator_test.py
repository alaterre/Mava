# python3
# Copyright 2021 InstaDeep Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Integration test of the evaluator for Jax-based Mava systems"""

import functools

import pytest

from mava.systems.jax import System
from mava.utils.environments import debugging_utils
from tests.jax.systems.systems_test_data import ippo_system_single_process

# Environment.
environment_factory = functools.partial(
    debugging_utils.make_environment,
    env_name="simple_spread",
    action_space="discrete",
)


@pytest.fixture
def test_system_sp() -> System:
    """A single process built system"""
    return ippo_system_single_process()


def test_evaluator_single_process(test_system_sp: System) -> None:
    """Test if the evaluator instantiates processes as expected."""
    (
        data_server,
        parameter_server,
        executor,
        evaluator,
        trainer,
    ) = test_system_sp._builder.store.system_build

    # Run an episode
    evaluator.run_episode()

    # Observe first (without adder)
    assert evaluator._executor.store.adder is None

    # Select actions and select action
    assert list(evaluator._executor.store.actions_info.keys()) == [
        "agent_0",
        "agent_1",
        "agent_2",
    ]
    assert list(evaluator._executor.store.policies_info.keys()) == [
        "agent_0",
        "agent_1",
        "agent_2",
    ]

    # check that the selected action is within the possible ones
    num_possible_actions = [
        environment_factory().action_spec()[agent].num_values
        for agent in environment_factory().possible_agents
    ]
    for i in range(len(num_possible_actions)):
        assert list(evaluator._executor.store.actions_info.values())[i] in range(
            0, num_possible_actions[i]
        )

    assert (
        lambda: key == "log_prob"
        for key in evaluator._executor.store.policies_info.values()
    )

    # Observe (without adder)
    assert not hasattr(evaluator._executor.store.adder, "add")
