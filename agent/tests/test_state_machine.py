from renderstudio_agent.state_machine import JobState, can_transition


def test_forward_flow_allowed():
    chain = [
        (JobState.PENDING, JobState.ASSIGNED),
        (JobState.ASSIGNED, JobState.PARSING),
        (JobState.PARSING, JobState.MODELING),
        (JobState.MODELING, JobState.MATERIAL),
        (JobState.MATERIAL, JobState.RENDERING),
        (JobState.RENDERING, JobState.COMPLETED),
    ]
    for frm, to in chain:
        assert can_transition(frm, to)


def test_terminal_states_cant_leave():
    for terminal in (JobState.COMPLETED, JobState.ERROR, JobState.CANCELLED):
        assert not can_transition(terminal, JobState.PENDING)
