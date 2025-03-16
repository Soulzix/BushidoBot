import os
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def run_command(command):
    try:
        # Don't log commands that might contain tokens
        sensitive_terms = ['remote add', 'clone', 'push', 'token', 'auth', 'password', 'secret']
        if not any(term in command for term in sensitive_terms):
            logger.debug(f"Running git command: {command}")
        else:
            logger.debug(f"Running sensitive git command (details redacted)")
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"Error output: {e.stderr}")
        raise

def setup_git():
    """Configure git if not already done"""
    try:
        # Configure git if not already done
        if not os.path.exists('.git'):
            run_command('git init')
            logger.info("Git repository initialized")

        # Configure git credentials using environment variables
        token = os.environ.get('GITHUB_TOKEN')
        repo = os.environ.get('GITHUB_REPOSITORY')

        if not token or not repo:
            raise ValueError("GitHub token or repository not set in environment variables")

        # Clean the repository string to ensure correct format
        repo = repo.replace('https://github.com/', '').replace('.git', '').strip()
        logger.info(f"Configuring for repository: {repo}")

        # Set git configurations
        run_command('git config --global user.name "Replit Sync"')
        run_command('git config --global user.email "sync@replit.com"')

        # Add remote repository with token authentication
        remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"

        # Check if remote exists and update it
        try:
            run_command('git remote remove origin')
        except:
            pass

        run_command(f'git remote add origin {remote_url}')
        logger.info("Git remote configured successfully")

        # Verify repository exists
        try:
            run_command('git ls-remote --exit-code')
            logger.info("Repository verification successful")
        except subprocess.CalledProcessError:
            logger.error("Failed to verify repository. Please check repository name and access token.")
            return False

        # Ensure we're on main branch
        try:
            run_command('git checkout main')
        except:
            run_command('git checkout -b main')

        return True
    except Exception as e:
        logger.error(f"Failed to setup git: {e}")
        return False

def sync_changes():
    """Sync changes to GitHub repository"""
    try:
        # Add all changes
        run_command('git add .')

        # Check if there are changes to commit
        try:
            run_command('git diff-index --quiet HEAD --')
            logger.info("No changes to sync")
            return True
        except subprocess.CalledProcessError:
            # Changes exist, proceed with commit
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            run_command(f'git commit -m "Auto-sync: {timestamp}"')

            # Push changes
            run_command('git push -u origin main --force')
            logger.info("Changes synced successfully")
            return True
    except Exception as e:
        if "nothing to commit" in str(e):
            logger.info("No changes to sync")
            return True
        logger.error(f"Failed to sync changes: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_git()
    sync_changes()