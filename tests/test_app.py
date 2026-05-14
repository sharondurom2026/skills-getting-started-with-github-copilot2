"""Test suite for Mergington High School API endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Arrange: No setup needed
        Act: Make GET request to root endpoint
        Assert: Should redirect to /static/index.html with 307 status
        """
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Arrange: Activities are loaded via fixture
        Act: Make GET request to /activities
        Assert: Should return all activities as dict
        """
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Club" in data
        assert "Science Club" in data

    def test_activity_structure_is_correct(self, client):
        """Arrange: Activities are loaded
        Act: Get activities and inspect structure
        Assert: Each activity should have required fields
        """
        response = client.get("/activities")
        data = response.json()
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_activity_data_types_are_correct(self, client):
        """Arrange: Activities are loaded
        Act: Get activities and check data types
        Assert: All fields should have correct types
        """
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_participants_contain_emails(self, client):
        """Arrange: Activities with participants are loaded
        Act: Get activities
        Assert: Participants should be email strings
        """
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Arrange: Basketball Team has no participants
        Act: Sign up new student
        Assert: Should return success message
        """
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Arrange: Soccer Club exists
        Act: Sign up student and then get activities
        Assert: Student should appear in participants list
        """
        email = "athlete@mergington.edu"
        client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": email}
        )
        
        # Verify signup was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Club"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Arrange: No activity called "Nonexistent Club"
        Act: Try to sign up for nonexistent activity
        Assert: Should return 404 error
        """
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_cannot_signup_twice_same_activity(self, client):
        """Arrange: Michael already signed up for Chess Club
        Act: Try to sign up same student again
        Assert: Should return 400 error
        """
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_with_special_characters_in_email(self, client):
        """Arrange: Basketball Team exists
        Act: Sign up with email containing special characters
        Assert: Should accept and add successfully
        """
        email = "student+tag@mergington.edu"
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify it was added
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Basketball Team"]["participants"]

    def test_signup_for_multiple_different_activities(self, client):
        """Arrange: Multiple activities exist
        Act: Sign up same student for different activities
        Assert: Student should appear in all activities
        """
        email = "versatile@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Basketball Team"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Arrange: Michael is signed up for Chess Club
        Act: Unregister from Chess Club
        Assert: Should return success message
        """
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client):
        """Arrange: Michael is signed up for Chess Club
        Act: Unregister and verify
        Assert: Student should no longer appear in participants
        """
        email = "michael@mergington.edu"
        client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Arrange: No "Nonexistent Club" activity
        Act: Try to unregister from nonexistent activity
        Assert: Should return 404 error
        """
        response = client.post(
            "/activities/Nonexistent%20Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_cannot_unregister_if_not_signed_up(self, client):
        """Arrange: Basketball Team is empty
        Act: Try to unregister student who never signed up
        Assert: Should return 404 error
        """
        response = client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": "noone@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_signup_after_unregister(self, client):
        """Arrange: Michael is signed up for Chess Club
        Act: Unregister then sign up again
        Assert: Should successfully re-register
        """
        email = "michael@mergington.edu"
        
        # Unregister first
        unregister_response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Sign up again
        signup_response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify re-signup
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]

    def test_unregister_with_multiple_participants(self, client):
        """Arrange: Chess Club has multiple participants
        Act: Unregister one student
        Assert: Others should remain, only one removed
        """
        response = client.get("/activities")
        data = response.json()
        original_participants = data["Chess Club"]["participants"].copy()
        assert len(original_participants) >= 2
        
        # Unregister one
        email_to_remove = original_participants[0]
        client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": email_to_remove}
        )
        
        # Verify only one was removed
        response = client.get("/activities")
        data = response.json()
        remaining = data["Chess Club"]["participants"]
        assert len(remaining) == len(original_participants) - 1
        assert email_to_remove not in remaining
        # Other participants should still be there
        for email in original_participants[1:]:
            assert email in remaining


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_complete_signup_and_unregister_workflow(self, client):
        """Arrange: New student ready to interact with activities
        Act: Sign up, verify, then unregister
        Assert: All operations should succeed with expected state changes
        """
        email = "integration@mergington.edu"
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_soccer_count = len(initial["Soccer Club"]["participants"])
        
        # Sign up
        signup_response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities").json()
        assert email in after_signup["Soccer Club"]["participants"]
        assert len(after_signup["Soccer Club"]["participants"]) == initial_soccer_count + 1
        
        # Unregister
        unregister_response = client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        final = client.get("/activities").json()
        assert email not in final["Soccer Club"]["participants"]
        assert len(final["Soccer Club"]["participants"]) == initial_soccer_count

    def test_concurrent_signups_for_same_activity(self, client):
        """Arrange: Multiple different students
        Act: Sign them up for the same activity
        Assert: All should be registered
        """
        activity = "Science%20Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        activities_data = client.get("/activities").json()
        for email in emails:
            assert email in activities_data["Science Club"]["participants"]

    def test_activity_with_spaces_in_name(self, client):
        """Arrange: Activity names contain spaces
        Act: Sign up for activity with spaces in name
        Assert: Should handle URL encoding correctly
        """
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "coder@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify
        activities_data = client.get("/activities").json()
        assert "coder@mergington.edu" in activities_data["Programming Class"]["participants"]
