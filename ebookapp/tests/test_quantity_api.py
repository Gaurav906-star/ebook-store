from django.test import TestCase
from unittest.mock import patch, MagicMock
import requests

from ebookapp.service import check_quantity_in_stock, LAMBDA_API


class TestCheckQuantity(TestCase):

    @patch("ebookapp.utils.requests.post")
    def test_check_quantity_success(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"available": True}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = check_quantity_in_stock(1, 5)

        mock_post.assert_called_once_with(
            LAMBDA_API,
            json={"book_id": 1, "requested_quantity": 5},
            timeout=5
        )
        self.assertEqual(result, {"available": True})

    @patch("ebookapp.utils.requests.post", side_effect=requests.exceptions.Timeout("Timeout"))
    def test_check_quantity_timeout(self, mock_post):
        result = check_quantity_in_stock(1, 5)
        self.assertEqual(result, {"error": "lambda function is timeout {e}"})

    @patch("ebookapp.utils.requests.post")
    def test_check_quantity_http_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad request")
        mock_post.return_value = mock_response

        result = check_quantity_in_stock(1, 5)
        self.assertEqual(result, {"error": "error in calling https request {e}"})

    @patch("ebookapp.utils.requests.post", side_effect=Exception("Something broke"))
    def test_check_quantity_generic_error(self, mock_post):
        result = check_quantity_in_stock(1, 5)
        self.assertEqual(result, {"error": "Something broke"})
