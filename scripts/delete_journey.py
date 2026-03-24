import database

def delete_journey_by_title(title):
    """Find and delete a journey by its title"""
    # Get all journeys
    all_journeys = database.get_all_journeys()
    
    # Find the journey with the specified title
    target_journey = None
    for journey in all_journeys:
        if journey['name'] == title:
            target_journey = journey
            break
    
    # If found, delete it
    if target_journey:
        journey_id = target_journey['id']
        print(f"Found journey with ID {journey_id} and title '{title}'")
        
        # Get waypoints associated with this journey
        waypoints = database.get_waypoints(journey_id)
        print(f"This journey has {len(waypoints)} waypoints")
        
        # Delete the journey (this will also delete all waypoints due to cascade)
        database.delete_journey(journey_id)
        print(f"Successfully deleted journey '{title}' with ID {journey_id}")
        return True
    else:
        print(f"No journey found with title '{title}'")
        return False

if __name__ == "__main__":
    title_to_delete = "Thabo Ndlovu's Conversation Journey"
    delete_journey_by_title(title_to_delete)
