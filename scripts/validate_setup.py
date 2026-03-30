#!/usr/bin/env python
"""Validation script for PromptGym setup."""

import sys
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_imports() -> Tuple[bool, List[str]]:
    """Check if all required imports are available."""
    issues = []
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "gymnasium",
        "numpy",
        "yaml",
    ]
    
    logger.info("Checking imports...")
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"  ✓ {module}")
        except ImportError:
            issues.append(f"Missing module: {module}")
            logger.error(f"  ✗ {module}")
    
    return len(issues) == 0, issues


def check_files() -> Tuple[bool, List[str]]:
    """Check if all required files exist."""
    import os
    
    issues = []
    required_files = [
        "app/main.py",
        "app/env/environment.py",
        "app/env/tasks.py",
        "app/env/grader.py",
        "app/utils/llm_executor.py",
        "app/agent/baseline_agent.py",
        "config.yaml",
        "requirements.txt",
        "Dockerfile",
        "README.md",
    ]
    
    logger.info("Checking files...")
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"  ✓ {file_path}")
        else:
            issues.append(f"Missing file: {file_path}")
            logger.error(f"  ✗ {file_path}")
    
    return len(issues) == 0, issues


def check_environment() -> Tuple[bool, List[str]]:
    """Check environment configuration."""
    import os
    import yaml
    
    issues = []
    
    logger.info("Checking environment...")
    
    # Check config.yaml
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            if config:
                logger.info("  ✓ config.yaml valid")
            else:
                issues.append("config.yaml is empty")
                logger.error("  ✗ config.yaml empty")
    except Exception as e:
        issues.append(f"config.yaml error: {str(e)}")
        logger.error(f"  ✗ config.yaml: {str(e)}")
    
    # Check if LLM provider is set
    provider = os.getenv("LLM_PROVIDER", "mock")
    if provider in ["mock", "openai"]:
        logger.info(f"  ✓ LLM_PROVIDER={provider}")
    else:
        issues.append(f"Unknown LLM_PROVIDER: {provider}")
        logger.error(f"  ✗ Unknown LLM_PROVIDER: {provider}")
    
    return len(issues) == 0, issues


def check_tasks() -> Tuple[bool, List[str]]:
    """Check task definitions."""
    import sys
    issues = []
    
    logger.info("Checking tasks...")
    
    try:
        from app.env.tasks import get_tasks
        
        tasks = get_tasks()
        if not tasks:
            issues.append("No tasks defined")
            logger.error("  ✗ No tasks found")
        else:
            logger.info(f"  ✓ Found {len(tasks)} tasks")
            
            # Check each difficulty
            difficulties = set(t.get("difficulty") for t in tasks)
            required = {"EASY", "MEDIUM", "HARD"}
            
            if required.issubset(difficulties):
                logger.info(f"  ✓ All difficulties present: {difficulties}")
            else:
                missing = required - difficulties
                issues.append(f"Missing difficulties: {missing}")
                logger.error(f"  ✗ Missing: {missing}")
    except Exception as e:
        issues.append(f"Failed to load tasks: {str(e)}")
        logger.error(f"  ✗ Error: {str(e)}")
    
    return len(issues) == 0, issues


def check_grader() -> Tuple[bool, List[str]]:
    """Check grader functionality."""
    issues = []
    
    logger.info("Checking grader...")
    
    try:
        from app.env.grader import grade_output
        
        # Test grading
        test_task = {
            "difficulty": "EASY",
            "expected_output": "Hello world"
        }
        
        score = grade_output(test_task, "Hello world")
        if 0 <= score <= 1:
            logger.info(f"  ✓ Grader works (test score: {score:.3f})")
        else:
            issues.append(f"Invalid score range: {score}")
            logger.error(f"  ✗ Score out of range: {score}")
    except Exception as e:
        issues.append(f"Grader error: {str(e)}")
        logger.error(f"  ✗ Error: {str(e)}")
    
    return len(issues) == 0, issues


def check_environment_init() -> Tuple[bool, List[str]]:
    """Check environment initialization."""
    issues = []
    
    logger.info("Checking environment initialization...")
    
    try:
        from app.env.environment import PromptGymEnv
        
        env = PromptGymEnv(llm_provider="mock")
        obs, info = env.reset()
        
        if obs and info:
            logger.info("  ✓ Environment initialized successfully")
            if "task_difficulty" in info:
                logger.info(f"  ✓ Loaded task: {info['task_difficulty']}")
            else:
                issues.append("Missing task_difficulty in info")
                logger.error("  ✗ Missing task_difficulty")
        else:
            issues.append("Environment returned empty observation/info")
            logger.error("  ✗ Empty response")
    except Exception as e:
        issues.append(f"Environment error: {str(e)}")
        logger.error(f"  ✗ Error: {str(e)}")
    
    return len(issues) == 0, issues


def check_api() -> Tuple[bool, List[str]]:
    """Check FastAPI application."""
    issues = []
    
    logger.info("Checking FastAPI application...")
    
    try:
        from app.main import app
        
        if app:
            logger.info("  ✓ FastAPI app loaded")
            
            # Check routes
            routes = [route.path for route in app.routes]
            required_routes = ["/health", "/reset", "/step", "/state", "/metrics", "/tasks"]
            
            for route in required_routes:
                if route in routes:
                    logger.info(f"  ✓ Route {route} present")
                else:
                    issues.append(f"Missing route: {route}")
                    logger.error(f"  ✗ Missing route: {route}")
        else:
            issues.append("Failed to load FastAPI app")
            logger.error("  ✗ App not loaded")
    except Exception as e:
        issues.append(f"FastAPI error: {str(e)}")
        logger.error(f"  ✗ Error: {str(e)}")
    
    return len(issues) == 0, issues


def main():
    """Run all checks."""
    logger.info("=" * 70)
    logger.info("PromptGym Validation Script")
    logger.info("=" * 70 + "\n")
    
    checks = [
        ("Imports", check_imports),
        ("Files", check_files),
        ("Environment", check_environment),
        ("Tasks", check_tasks),
        ("Grader", check_grader),
        ("Environment Init", check_environment_init),
        ("FastAPI", check_api),
    ]
    
    results = []
    all_issues = []
    
    for name, check_func in checks:
        try:
            success, issues = check_func()
            results.append((name, success))
            if issues:
                all_issues.extend([(name, issue) for issue in issues])
        except Exception as e:
            logger.error(f"Check '{name}' crashed: {str(e)}")
            results.append((name, False))
            all_issues.append((name, f"Crash: {str(e)}"))
        
        logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status} - {name}")
    
    logger.info("")
    logger.info(f"Result: {passed}/{total} checks passed")
    
    if all_issues:
        logger.info("\nIssues found:")
        for component, issue in all_issues:
            logger.error(f"  [{component}] {issue}")
        
        logger.info("")
        logger.error("Fix issues and run validation again.")
        return 1
    else:
        logger.info("\n✓ All validation checks passed! Ready for deployment.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
