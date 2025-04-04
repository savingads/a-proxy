import os
import requests
import logging
from datetime import datetime
import database

logger = logging.getLogger(__name__)

def reset_rate_limit_if_needed():
    """
    Reset the Internet Archive submission counter if it's a new day
    
    Returns:
        bool: True if counter was reset, False otherwise
    """
    last_reset = database.get_setting('internet_archive_last_reset', datetime.now().strftime('%Y-%m-%d'))
    today = datetime.now().strftime('%Y-%m-%d')
    
    if last_reset != today:
        database.set_setting('internet_archive_submissions_today', '0')
        database.set_setting('internet_archive_last_reset', today)
        logger.info(f"Reset Internet Archive submission counter for new day: {today}")
        return True
    
    return False

def check_rate_limit():
    """
    Check if we've exceeded the Internet Archive submission rate limit
    
    Returns:
        tuple: (bool, int, int) - (can_submit, submissions_today, rate_limit)
    """
    # Reset counter if it's a new day
    reset_rate_limit_if_needed()
    
    # Get current values
    submissions_today = int(database.get_setting('internet_archive_submissions_today', '0'))
    rate_limit = int(database.get_setting('internet_archive_rate_limit', '10'))
    
    # Check if we're under the limit
    can_submit = submissions_today < rate_limit
    
    return (can_submit, submissions_today, rate_limit)

def increment_submission_counter():
    """
    Increment the Internet Archive submission counter
    
    Returns:
        int: The new counter value
    """
    # Get current value
    submissions_today = int(database.get_setting('internet_archive_submissions_today', '0'))
    
    # Increment and save
    new_value = submissions_today + 1
    database.set_setting('internet_archive_submissions_today', str(new_value))
    
    return new_value

def submit_to_internet_archive(url):
    """
    Submit a URL to the Internet Archive for archiving
    
    Args:
        url: The URL to archive
    
    Returns:
        tuple: (success, archived_url or error_message)
    """
    # Check if Internet Archive integration is enabled
    ia_enabled = database.get_setting('internet_archive_enabled', 'true').lower() == 'true'
    if not ia_enabled:
        return (False, "Internet Archive integration is disabled")
    
    # Check rate limit
    can_submit, submissions_today, rate_limit = check_rate_limit()
    if not can_submit:
        return (False, f"Rate limit exceeded: {submissions_today}/{rate_limit} submissions today")
    
    # Submit to Internet Archive
    ia_url = f"https://web.archive.org/save/{url}"
    
    try:
        logger.info(f"Submitting URL to Internet Archive: {url}")
        
        # Make the request to the Internet Archive
        response = requests.get(ia_url, timeout=30)
        
        # Handle the response
        if response.status_code >= 200 and response.status_code < 300:
            # Success - increment counter
            increment_submission_counter()
            
            # The archived URL should be available at:
            archived_url = f"https://web.archive.org/web/{datetime.now().strftime('%Y%m%d%H%M%S')}/{url}"
            
            # If there's a memento header, use that instead
            memento_datetime = response.headers.get('Memento-Datetime')
            
            # The actual URL will be in the Location header if redirected
            if 'Location' in response.headers:
                archived_url = response.headers['Location']
            
            logger.info(f"Successfully archived URL: {archived_url}")
            return (True, archived_url)
        else:
            error_msg = f"Failed to archive URL: {response.status_code} - {response.text[:500]}"
            logger.error(error_msg)
            return (False, error_msg)
    
    except Exception as e:
        error_msg = f"Error submitting URL to Internet Archive: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def update_memento_with_ia_url(memento_id, ia_url):
    """
    Update a memento with the Internet Archive URL
    
    Args:
        memento_id: The ID of the memento
        ia_url: The Internet Archive URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE mementos SET internet_archive_id = ? WHERE id = ?",
            (ia_url, memento_id)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating memento with Internet Archive URL: {str(e)}")
        return False
