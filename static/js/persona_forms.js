// Persona forms handling JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set up the behavioral form
    setupBehavioralForm();
    
    // Set up the contextual form
    setupContextualForm();
    
    // Initialize form IDs when selecting a persona
    document.querySelectorAll('.select-persona-btn').forEach(button => {
        button.addEventListener('click', function() {
            const personaId = this.getAttribute('data-persona-id');
            document.getElementById('psychographic-persona-id').value = personaId;
            document.getElementById('behavioral-persona-id').value = personaId;
            document.getElementById('contextual-persona-id').value = personaId;
        });
    });
});

function setupBehavioralForm() {
    // Create the behavioral form if it doesn't exist
    if (!document.getElementById('behavioral-form')) {
        const behaviorTab = document.getElementById('behavior');
        if (behaviorTab) {
            const container = behaviorTab.querySelector('.container');
            if (container) {
                const card = document.createElement('div');
                card.className = 'custom-card';
                card.innerHTML = `
                    <h4>Behavioral Data</h4>
                    <form action="${getUrlFor('persona.save_behavioral_data')}" method="post" id="behavioral-form">
                        <input type="hidden" name="persona_id" id="behavioral-persona-id" value="">

                        <div class="mb-3">
                            <label for="browsing_habits" class="form-label">Browsing Habits (comma separated)</label>
                            <input type="text" class="form-control" id="browsing_habits" name="browsing_habits"
                                placeholder="social media, news, research">
                        </div>

                        <div class="mb-3">
                            <label for="purchase_history" class="form-label">Purchase History (comma separated)</label>
                            <input type="text" class="form-control" id="purchase_history" name="purchase_history"
                                placeholder="electronics, clothing, books">
                        </div>

                        <div class="mb-3">
                            <label for="online_activity" class="form-label">Online Activity</label>
                            <input type="text" class="form-control" id="online_activity" name="online_activity"
                                placeholder="daily social media, weekly shopping">
                        </div>

                        <div class="mb-3">
                            <label for="content_consumption" class="form-label">Content Consumption</label>
                            <input type="text" class="form-control" id="content_consumption" name="content_consumption"
                                placeholder="video streaming, podcasts, articles">
                        </div>

                        <div class="mb-3">
                            <label for="tech_usage" class="form-label">Technology Usage</label>
                            <input type="text" class="form-control" id="tech_usage" name="tech_usage"
                                placeholder="mobile-first, desktop for work">
                        </div>

                        <button type="submit" class="btn btn-primary">Save Behavioral Data</button>
                    </form>
                `;
                container.appendChild(card);
            }
        }
    }
}

function setupContextualForm() {
    // Create the contextual form if it doesn't exist
    if (!document.getElementById('contextual-form')) {
        const contextualTab = document.getElementById('contextual');
        if (contextualTab) {
            const container = contextualTab.querySelector('.container');
            if (container) {
                const card = document.createElement('div');
                card.className = 'custom-card';
                card.innerHTML = `
                    <h4>Contextual Data</h4>
                    <form action="${getUrlFor('persona.save_contextual_data')}" method="post" id="contextual-form">
                        <input type="hidden" name="persona_id" id="contextual-persona-id" value="">

                        <div class="mb-3">
                            <label for="device" class="form-label">Device</label>
                            <select class="form-select" id="device" name="device">
                                <option value="" disabled selected>Select a device</option>
                                <option value="desktop">Desktop</option>
                                <option value="laptop">Laptop</option>
                                <option value="tablet">Tablet</option>
                                <option value="mobile">Mobile</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="time_of_day" class="form-label">Time of Day</label>
                            <select class="form-select" id="time_of_day" name="time_of_day">
                                <option value="" disabled selected>Select time of day</option>
                                <option value="morning">Morning</option>
                                <option value="afternoon">Afternoon</option>
                                <option value="evening">Evening</option>
                                <option value="night">Night</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="location_type" class="form-label">Location Type</label>
                            <select class="form-select" id="location_type" name="location_type">
                                <option value="" disabled selected>Select location type</option>
                                <option value="home">Home</option>
                                <option value="work">Work</option>
                                <option value="public">Public Space</option>
                                <option value="commuting">Commuting</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="network_type" class="form-label">Network Type</label>
                            <select class="form-select" id="network_type" name="network_type">
                                <option value="" disabled selected>Select network type</option>
                                <option value="home_wifi">Home Wi-Fi</option>
                                <option value="work_wifi">Work Wi-Fi</option>
                                <option value="public_wifi">Public Wi-Fi</option>
                                <option value="mobile_data">Mobile Data</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="browser" class="form-label">Browser</label>
                            <select class="form-select" id="browser" name="browser">
                                <option value="" disabled selected>Select browser</option>
                                <option value="chrome">Chrome</option>
                                <option value="firefox">Firefox</option>
                                <option value="safari">Safari</option>
                                <option value="edge">Edge</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary">Save Contextual Data</button>
                    </form>
                `;
                container.appendChild(card);
            }
        }
    }
}

// Helper function to get URL for a route
function getUrlFor(routeName) {
    // This is a placeholder - in a real application, you would use Flask's url_for 
    // Since we can't access Flask's url_for directly in a static JS file,
    // we're using this as a workaround
    return `/persona/${routeName.split('.')[1]}`;
}
