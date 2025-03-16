import os
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def run_command(command):
    try:
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"Error output: {e.stderr}")
        raise

def setup_git():
    # Configure git if not already done
    if not os.path.exists('.git'):
        run_command('git init')
        logger.info("Git repository initialized")

    # Configure git credentials using environment variables
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    
    if not token or not repo:
        raise ValueError("GitHub token or repository not set in environment variables")

    # Set git configurations
    run_command('git config --global user.name "Replit Sync"')
    run_command('git config --global user.email "sync@replit.com"')
    
    # Add remote repository with token authentication
    remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    
    # Check if remote exists
    try:
        run_command('git remote remove origin')
    except:
        pass
    
    run_command(f'git remote add origin {remote_url}')
    logger.info("Git remote configured successfully")

def sync_changes():
    try:
        # Add all changes
        run_command('git add .')
        
        # Create commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_command(f'git commit -m "Auto-sync: {timestamp}"')
        
        # Push changes
        run_command('git push -u origin main --force')
        logger.info("Changes synced successfully")
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e.stderr):
            logger.info("No changes to sync")
        else:
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_git()
    sync_changes()
