from unittest.mock import patch, MagicMock
from ebookapp.service import check_quantity_in_stock   # adjust import based on your file location

# SUCCESS CASE
@patch("ebookapp.utils.requests.post")
def test_check_quantity_success(mock_post):
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"available": True, "quantity": 10}
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    # Act
    result = check_quantity_in_stock(book_id=1, requested_quantity=2)

    # Assert
    assert result == {"available": True, "quantity": 10}
    mock_post.assert_called_once_with(
        'https://bz5cga6tkc.execute-api.us-east-1.amazonaws.com/prod/api/checkforquantity',
        json={"book_id": 1, "requested_quantity": 2},
        timeout=5
    )


# TIMEOUT CASE
@patch("ebookapp.utils.requests.post")
def test_check_quantity_timeout(mock_post):
    mock_post.side_effect = Exception("timeout")

    result = check_quantity_in_stock(1, 5)

    assert "error" in result
    assert "timeout" in result["error"]


# HTTP ERROR CASE
@patch("ebookapp.utils.requests.post")
def test_check_quantity_http_error(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")

    mock_post.return_value = mock_response

    result = check_quantity_in_stock(1, 5)

    assert "error" in result
    assert "HTTP error" in result["error"]
