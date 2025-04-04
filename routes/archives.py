from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import database
import os
import logging
from utils import internet_archive

archives_bp = Blueprint('archives', __name__)

@archives_bp.route("/archives")
def list_archives():
    """List all archived websites."""
    archived_websites = database.get_all_archived_websites()
    return render_template("archives.html", archived_websites=archived_websites)

@archives_bp.route("/archives/<int:archived_website_id>")
def view_archive(archived_website_id):
    """View a specific archived website and its mementos."""
    archived_website = database.get_archived_website(archived_website_id)
    if not archived_website:
        flash("Archived website not found.", "danger")
        return redirect(url_for('archives.list_archives'))
    
    mementos = database.get_mementos_for_website(archived_website_id)
    return render_template("archive_detail.html", archived_website=archived_website, mementos=mementos)

@archives_bp.route("/archives/<int:archived_website_id>/mementos/<int:memento_id>")
def view_memento(archived_website_id, memento_id):
    """View a specific memento."""
    archived_website = database.get_archived_website(archived_website_id)
    if not archived_website:
        flash("Archived website not found.", "danger")
        return redirect(url_for('archives.list_archives'))
    
    memento = database.get_memento(memento_id)
    if not memento or memento['archived_website_id'] != archived_website_id:
        flash("Memento not found.", "danger")
        return redirect(url_for('archives.view_archive', archived_website_id=archived_website_id))
    
    # Check if the memento HTML file exists
    html_file_path = os.path.join(memento['memento_location'], 'content.html')
    if os.path.exists(html_file_path):
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        html_content = "<p>HTML content not available.</p>"
    
    return render_template("memento_viewer.html", 
                          archived_website=archived_website, 
                          memento=memento, 
                          html_content=html_content)

@archives_bp.route("/delete-archive/<int:archived_website_id>", methods=["POST"])
def delete_archive(archived_website_id):
    """Delete an archived website and all its associated mementos."""
    try:
        # Get the archive info first for the success message
        archived_website = database.get_archived_website(archived_website_id)
        if not archived_website:
            flash("Archived website not found.", "danger")
            return redirect(url_for('archives.list_archives'))
        
        # Delete the archived website (which also deletes all related mementos)
        database.delete_archived_website(archived_website_id)
        
        flash(f"Archive of {archived_website['uri_r']} and all associated mementos have been deleted successfully.", "success")
        return redirect(url_for('archives.list_archives'))
    
    except Exception as e:
        logging.error(f"Error deleting archived website: {e}")
        flash(f"Error deleting archived website: {str(e)}", "danger")
        return redirect(url_for('archives.list_archives'))

@archives_bp.route("/submit-to-internet-archive/<int:memento_id>", methods=["POST"])
def submit_to_internet_archive(memento_id):
    """Submit a memento to the Internet Archive."""
    try:
        # Get the memento
        memento = database.get_memento(memento_id)
        if not memento:
            flash("Memento not found.", "danger")
            return redirect(url_for('archives.list_archives'))
        
        # Check if already submitted
        if memento.get('internet_archive_id'):
            flash("This page has already been submitted to the Internet Archive.", "info")
            return redirect(url_for('archives.view_archive', archived_website_id=memento['archived_website_id']))
        
        # Submit to Internet Archive
        success, result = internet_archive.submit_to_internet_archive(memento['uri_r'])
        
        if success:
            # Update the memento with the Internet Archive ID
            internet_archive.update_memento_with_ia_url(memento_id, result)
            flash("Successfully submitted to the Internet Archive.", "success")
        else:
            flash(f"Failed to submit to Internet Archive: {result}", "danger")
        
        return redirect(url_for('archives.view_archive', archived_website_id=memento['archived_website_id']))
    
    except Exception as e:
        logging.error(f"Error submitting to Internet Archive: {e}")
        flash(f"Error submitting to Internet Archive: {str(e)}", "danger")
        return redirect(url_for('archives.list_archives'))

@archives_bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Manage archive settings."""
    if request.method == "POST":
        # Update settings
        ia_enabled = request.form.get('internet_archive_enabled', 'false') == 'on'
        ia_rate_limit = request.form.get('internet_archive_rate_limit', '10')
        
        # Validate rate limit
        try:
            rate_limit = int(ia_rate_limit)
            if rate_limit < 1:
                rate_limit = 1
            elif rate_limit > 100:
                rate_limit = 100
        except ValueError:
            rate_limit = 10
        
        # Save settings
        database.set_setting('internet_archive_enabled', 'true' if ia_enabled else 'false')
        database.set_setting('internet_archive_rate_limit', str(rate_limit))
        
        flash("Settings updated successfully.", "success")
    
    # Get current settings
    settings = {
        'internet_archive_enabled': database.get_setting('internet_archive_enabled', 'true') == 'true',
        'internet_archive_rate_limit': int(database.get_setting('internet_archive_rate_limit', '10')),
        'internet_archive_submissions_today': int(database.get_setting('internet_archive_submissions_today', '0'))
    }
    
    return render_template("archive_settings.html", settings=settings)

@archives_bp.route("/api/internet-archive-status", methods=["GET"])
def get_internet_archive_status():
    """API endpoint to get Internet Archive status information."""
    # Reset counter if it's a new day
    internet_archive.reset_rate_limit_if_needed()
    
    # Get current values
    submissions_today = int(database.get_setting('internet_archive_submissions_today', '0'))
    rate_limit = int(database.get_setting('internet_archive_rate_limit', '10'))
    enabled = database.get_setting('internet_archive_enabled', 'true') == 'true'
    can_submit = enabled and submissions_today < rate_limit
    
    return jsonify({
        'enabled': enabled,
        'submissions_today': submissions_today,
        'rate_limit': rate_limit,
        'can_submit': can_submit,
        'remaining': max(0, rate_limit - submissions_today)
    })
