import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

app = app_module.app

# Capture the initial state so we can reset before each test
_INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure each test starts with a fresh in-memory activities store."""
    app_module.activities = copy.deepcopy(_INITIAL_ACTIVITIES)
    yield


def test_get_activities_contains_chess_club():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_works_once_then_fails_on_duplicate():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    signup_path = "/activities/Chess%20Club/signup"

    # Act (first signup)
    first_response = client.post(signup_path, params={"email": email})

    # Assert (first signup succeeded)
    assert first_response.status_code == 200
    assert "Signed up" in first_response.json()["message"]

    # Act (duplicate signup)
    second_response = client.post(signup_path, params={"email": email})

    # Assert (duplicate fails)
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_them():
    # Arrange
    client = TestClient(app)
    target_email = "michael@mergington.edu"
    delete_path = "/activities/Chess%20Club/participants"

    # Sanity check: participant exists before deletion
    before = client.get("/activities").json()
    assert target_email in before["Chess Club"]["participants"]

    # Act (delete participant)
    delete_response = client.delete(delete_path, params={"email": target_email})

    # Assert (delete works)
    assert delete_response.status_code == 200
    assert f"Removed {target_email}" in delete_response.json()["message"]

    # Verify participant removed
    after = client.get("/activities").json()
    assert target_email not in after["Chess Club"]["participants"]
