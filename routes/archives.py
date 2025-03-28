from flask import Blueprint, render_template, redirect, url_for, flash
import database
import os
import logging

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
