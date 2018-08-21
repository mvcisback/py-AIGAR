from aiger import atom
from aiger_analysis.safety_game import Game


def test_true():
    assert not Game(atom(True).aig).is_realizable()


def test_false():
    assert Game(atom(False).aig).is_realizable()


system, environment = atom('controllable_x'), atom('env')


def test_system():
    assert Game(system.aig).is_realizable()
    assert Game((~system).aig).is_realizable()


def test_env():
    assert not Game(environment.aig).is_realizable()
    assert not Game((~environment).aig).is_realizable()


def test_system_delay():
    system_delay = system.aig | atom('out').aig
    system_delay = system_delay.feedback(inputs=atom('out').aig.inputs,
                                         outputs=[system.output],
                                         initials=[True],
                                         keep_outputs=False)
    assert Game(system_delay).is_realizable()


def test_env_delay():
    env_delay = environment.aig | atom('out').aig
    env_delay = env_delay.feedback(inputs=atom('out').aig.inputs,
                                   outputs=[environment.output],
                                   initials=[True],
                                   keep_outputs=False)
    assert not Game(env_delay).is_realizable()


def test_game_equal():
    equal = system == environment
    assert Game(equal.aig).is_realizable()
