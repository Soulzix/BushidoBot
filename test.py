"""
GitHub Sync Test Module for BushidoBot
Verifies the functionality of automatic GitHub synchronization.
Tests repository configuration and sync operations.
"""

import logging
import os
from git_sync import setup_git, sync_changes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_github_sync():
    """Test GitHub synchronization functionality"""
    try:
        # Check if required environment variables are set
        token = os.environ.get('GITHUB_TOKEN')
        repo = os.environ.get('GITHUB_REPOSITORY')

        if not token or not repo:
            logger.error("Missing required environment variables (GITHUB_TOKEN or GITHUB_REPOSITORY)")
            return False

        logger.info(f"Testing GitHub sync for repository: {repo}")

        # Test git setup
        if not setup_git():
            logger.error("Git setup failed")
            return False
        logger.info("Git setup successful")

        # Test sync changes
        if not sync_changes():
            logger.error("Sync changes failed")
            return False
        logger.info("Sync changes successful")

        return True

    except Exception as e:
        logger.error(f"Error during GitHub sync test: {e}")
        return False

if __name__ == "__main__":
    print("Starting GitHub sync test...")
    result = test_github_sync()
    print(f"Test {'succeeded' if result else 'failed'}")