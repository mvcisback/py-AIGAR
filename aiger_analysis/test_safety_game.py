from aiger import atom
from aiger_analysis.safety_game import Game


def test_true():
    assert not Game(atom(True).aig).is_realizable()


def test_false():
    assert Game(atom(False).aig).is_realizable()


system, environment = atom('controllable_variable'), atom('env')


def test_system():
    assert Game(system.aig).is_realizable()
    assert Game((~system).aig).is_realizable()


def test_env():
    assert not Game(environment.aig).is_realizable()
    assert not Game((~environment).aig).is_realizable()


def test_latch_initialization_true():
    latch = atom('latch').aig
    game_true = latch.feedback(inputs=latch.inputs,
                               outputs=latch.outputs,
                               initials=[True],
                               keep_outputs=True)
    assert not Game(game_true).is_realizable()


def test_latch_initialization_false():
    latch = atom('latch').aig
    game_false = latch.feedback(inputs=latch.inputs,
                                outputs=latch.outputs,
                                initials=[False],
                                keep_outputs=True)
    print(game_false)
    assert Game(game_false).is_realizable()


def test_system_delay():
    tmp = system.aig | atom('latch').aig
    system_delay = tmp.feedback(inputs=atom('latch').aig.inputs,
                                outputs=[system.output],
                                initials=[False],
                                keep_outputs=False)
    assert Game(system_delay).is_realizable()


def test_env_delay():
    tmp = environment.aig | atom('latch').aig
    env_delay = tmp.feedback(inputs=atom('latch').aig.inputs,
                             outputs=[environment.output],
                             initials=[False],
                             keep_outputs=False)
    assert not Game(env_delay).is_realizable()


def test_game_equal():
    equal = system == environment
    assert Game(equal.aig).is_realizable()
