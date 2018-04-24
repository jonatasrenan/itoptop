from .datamodel import DataModel
from .exceptions import ItopError
from .schema import Schema
import requests
import json


class Itop(object):
    url = version = auth_user = auth_pwd = auth = data_model = None

    def __init__(self, url, version, auth_user, auth_pwd, data_model=None):
        """
        Create connection.
        :param url: iTop rest.php endpoint
        :param version: API version
        :param auth_user: User
        :param auth_pwd: Password
        """
        self.url = url
        self.version = version
        self.auth_user = auth_user
        self.auth_pwd = auth_pwd
        data = {
            'operation': 'core/check_credentials',
            'user': self.auth_user,
            'password': self.auth_pwd
        }
        self.request(data)

        if data_model:
            self.data_model = DataModel(data_model)
            for schema in self.data_model.schemas:
                setattr(self, schema, Schema(self, schema))

    def request(self, data):
        """
        Generic request to iTop API
        :param data: Valid Data to iTop
        :return: Result objects
        """
        json_data = json.dumps(data)

        try:
            response = requests.post(
                self.url,
                data={
                    'version': self.version,
                    'auth_user': self.auth_user,
                    'auth_pwd': self.auth_pwd,
                    'json_data': json_data
                }
            )
            json_return = json.loads(response.content.decode('utf-8'))
            return_code = json_return['code']
            response.raise_for_status()
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema) as e:
            raise type(e)('Connection adapters (http:// or https://) is invalid: %s. ' % self.url + str(e.message))
        except requests.exceptions.ConnectionError as e:
            raise type(e)('Connection refused. ' + str(e))
        except requests.exceptions.HTTPError as e:
            raise type(e)("Could not connect. HTTP code %s. " % response.status_code + str(e))
        except ValueError as e:
            e.msg = e.msg
            raise type(e)('Not a valid JSON, maybe the page is returning other data: ' + str(e.msg), "", 0)

        if return_code is not 0:
            raise ItopError(response=response)

        if 'objects' not in json_return or json_return['objects'] is None:
            return []

        clean_objects = list(json_return['objects'].values()) if 'objects' in json_return else []
        clean_objects = [{**obj['fields'], **{'id': obj['key']}} for obj in clean_objects]

        if 'output_fields' in data:
            if len(data['output_fields'].split(', ')) > 1 and data['output_fields'] != '*':
                clean_objects = []
        return clean_objects

    def schema(self, name):
        """
        Get a specific schema from iTop to manipulate with find, create, update, remove, sync methods.
        :param name: Schema name
        :return: Schema object
        """
        return Schema(self, name)
