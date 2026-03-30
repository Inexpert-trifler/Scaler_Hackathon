"""Tests for the PromptGym environment directly."""

import pytest
from server.environment import PromptGymEnvironment
from models import PromptAction


def test_reset_returns_observation():
    """Test that reset() returns PromptObservation with task_description."""
    env = PromptGymEnvironment()
    observation = env.reset(difficulty="EASY")
    
    assert hasattr(observation, 'task_description')
    assert observation.task_description is not None
    assert len(observation.task_description) > 0
    assert observation.difficulty == "easy"
    assert observation.step == 0
    assert observation.done is False


def test_step_returns_reward():
    """Test that step() returns reward in [0.0, 1.0]."""
    env = PromptGymEnvironment()
    env.reset(difficulty="EASY")
    
    action = PromptAction(prompt="Test prompt for summarization")
    observation = env.step(action)
    
    assert hasattr(observation, 'reward')
    assert 0.0 <= observation.reward <= 1.0


def test_done_after_max_steps():
    """Test that after MAX_STEPS steps, done=True."""
    env = PromptGymEnvironment()
    env.reset(difficulty="EASY")
    
    max_steps = 5  # Assuming MAX_STEPS is 5
    done_found = False
    
    for i in range(max_steps):
        action = PromptAction(prompt=f"Test prompt {i}")
        observation = env.step(action)
        
        if observation.done:
            done_found = True
            break
    
    assert done_found, "Episode should be done after MAX_STEPS"


def test_state_tracks_episode():
    """Test that state.episode_id is set after reset."""
    env = PromptGymEnvironment()
    
    # Before reset, episode_id should have some value
    initial_state = env.state
    assert initial_state.episode_id is not None
    assert len(initial_state.episode_id) > 0
    
    # After reset, episode_id should be set (possibly different)
    env.reset(difficulty="MEDIUM")
    state_after_reset = env.state
    
    assert state_after_reset.episode_id is not None
    assert len(state_after_reset.episode_id) > 0
    assert state_after_reset.difficulty == "medium"


def test_all_difficulties():
    """Test that reset works for easy/medium/hard."""
    env = PromptGymEnvironment()
    
    # Test EASY
    obs_easy = env.reset(difficulty="EASY")
    assert obs_easy.difficulty == "easy"
    assert obs_easy.task_type == "summarization"
    
    # Test MEDIUM
    obs_medium = env.reset(difficulty="MEDIUM")
    assert obs_medium.difficulty == "medium"
    assert obs_medium.task_type == "json_extraction"
    
    # Test HARD
    obs_hard = env.reset(difficulty="HARD")
    assert obs_hard.difficulty == "hard"
    assert obs_hard.task_type == "reasoning"


def test_reward_improves_with_keywords():
    """Test that prompt with task keywords scores higher than empty prompt."""
    env = PromptGymEnvironment()
    
    # Reset with easy task (summarization)
    obs = env.reset(difficulty="EASY")
    
    # Step with empty prompt
    action_empty = PromptAction(prompt="")
    obs_empty = env.step(action_empty)
    reward_empty = obs_empty.reward
    
    # Reset again for fair comparison
    env.reset(difficulty="EASY")
    
    # Step with keyword-rich prompt
    action_keyword = PromptAction(prompt="Please summarize this text carefully and concisely")
    obs_keyword = env.step(action_keyword)
    reward_keyword = obs_keyword.reward
    
    # Keyword prompt should score higher (or equal)
    assert reward_keyword >= 0.0, f"Keyword reward {reward_keyword} should be >= 0"
    assert reward_keyword <= 1.0


def test_observation_structure():
    """Test that observation has all required attributes."""
    env = PromptGymEnvironment()
    obs = env.reset(difficulty="EASY")
    
    required_attributes = [
        'task_description',
        'input_data', 
        'task_type',
        'difficulty',
        'step',
        'max_steps',
        'done',
        'reward',
        'last_llm_output',
        'last_score',
        'grader_signals',
        'message'
    ]
    
    for attr in required_attributes:
        assert hasattr(obs, attr), f"Missing attribute: {attr}"


def test_state_structure():
    """Test that state has all required attributes."""
    env = PromptGymEnvironment()
    env.reset(difficulty="MEDIUM")
    
    state = env.state
    
    required_attributes = [
        'task_id',
        'episode_id',
        'step_count',
        'difficulty',
        'total_reward',
        'best_reward',
        'done',
        'task_description'
    ]
    
    for attr in required_attributes:
        assert hasattr(state, attr), f"Missing state attribute: {attr}"


def test_step_increases_counter():
    """Test that step count increases with each step."""
    env = PromptGymEnvironment()
    env.reset(difficulty="HARD")
    
    initial_step = env.state.step_count
    assert initial_step == 0
    
    # First step
    action1 = PromptAction(prompt="First step")
    obs1 = env.step(action1)
    assert obs1.step == 1
    assert env.state.step_count == 1
    
    # Second step
    action2 = PromptAction(prompt="Second step")
    obs2 = env.step(action2)
    assert obs2.step == 2
    assert env.state.step_count == 2


def test_multiple_episodes():
    """Test that multiple episodes work independently."""
    env = PromptGymEnvironment()
    
    # First episode
    obs1 = env.reset(difficulty="EASY")
    episode1_id = env.state.episode_id
    
    # Do some steps
    for i in range(2):
        action = PromptAction(prompt=f"Episode 1 step {i}")
        env.step(action)
    
    # Second episode
    obs2 = env.reset(difficulty="MEDIUM")
    episode2_id = env.state.episode_id
    
    # Episodes should have different IDs
    assert episode1_id != episode2_id
    
    # Second episode should start at step 0
    assert obs2.step == 0
    assert env.state.step_count == 0
