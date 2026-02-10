import json

from django.test.client import RequestFactory
from marshmallow import Schema, fields

from bereikbaarheid.wrapper import extract_parameters, geo_json_response, validate_data


class MockValidation(Schema):
    message = fields.Str(required=True)
    code = fields.Int(required=True)


class MockResponse:
    status_code = 200


class TestWrappers:
    @validate_data(MockValidation)
    def fake_view_post(self, request, serialized_data, *args, **kwargs):
        return MockResponse()

    @geo_json_response
    def fake_view_geo(self, request, data):
        return data

    def test_validate_data(self):
        request = RequestFactory().post("/", data={"message": "test", "code": 111}, content_type="application/json")
        response = self.fake_view_post(request)
        assert response.status_code == 200

    def test_validate_data_incorrect_parameters(self):
        request = RequestFactory().post(
            "/",
            data={"message": "test", "code": "milk"},
            content_type="application/json",
        )
        response = self.fake_view_post(request)
        assert response.status_code == 400

    def test_validate_data_invalid_parameters(self):
        request = RequestFactory().post("/", data={"message": "test", "code": "milk"})
        response = self.fake_view_post(request)
        assert response.status_code == 400

    def test_extract_parameters_post_request(self):
        """
        Extract data from the request using the POST method
        and transform it to a dict
        :return:
        """
        data = {"message": "test", "code": "milk"}
        request = RequestFactory().post(
            "/",
            data={"message": "test", "code": "milk"},
            content_type="application/json",
        )

        result = extract_parameters(request)
        assert result == data

    def test_extract_parameters_get_request(self):
        """
        Extract data from the request using the GET method
        and transform it to a dict
        :return:
        """
        data = {"message": "test", "code": "111"}
        request = RequestFactory().get("/?message=test&code=111")

        result = extract_parameters(request)
        assert result == data

    def test_geo_json_response(self):
        data = {"some": "fake_data"}
        result = self.fake_view_geo(request="fake", data=data)
        assert result.status_code == 200
        assert json.loads(result.content) == {
            "features": data,
            "type": "FeatureCollection",
        }
