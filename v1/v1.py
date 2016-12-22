import requests
import base64
import urllib


class V1:
    def __init__(self, hostname, instance, port=80, is_https=False):
        self.hostname = hostname
        self.instance = instance
        self.port = str(port)
        self.protocol = "https" if is_https else "http"

    def with_access_token(self, token):
        return Meta(self.hostname, self.instance, self.protocol, self.port, token, False)

    def with_creds(self, username, password):
        token = base64.b64encode(username + ":" + password)
        return Meta(self.hostname, self.instance, self.protocol, self.port, token, True)


class Oid:
    def __init__(self, oid_token):
        oid_parts = oid_token.split(":")
        self.asset_type = oid_parts[0]
        self.number = oid_parts[1]

    def __str__(self):
        return self.asset_type + ":" + self.number


class Meta:
    def __init__(self, hostname, instance, protocol, port, token, is_basic):
        self.urls = get_v1_urls(hostname, instance, protocol, port)
        self.headers = create_header_objects(token, is_basic)

    def create(self, asset_type, asset_data):
        post_data = transform_data_to_asset(asset_data)
        url = self.urls["rest"] + '/' + asset_type
        return requests.post(url=url, data=post_data, headers=self.headers)

    def update(self, oid_token, asset_data, change_comment):
        oid = Oid(oid_token)
        post_data = transform_data_to_asset(asset_data)
        comment = "?comment={0}".format(urllib.quote(change_comment, safe="")) if change_comment else ""
        url = self.urls["rest"] + "/" + oid.asset_type + "/" + oid.number + comment
        return requests.post(url=url, data=post_data, headers=self.headers)

    def query(self, query):
        return requests.post(url=self.urls["query"], data=query, headers=self.headers)

    def execute_operation(self, oid_token, operation_name):
        oid = Oid(oid_token)
        url = self.urls["rest"] + "/" + oid.asset_type + "/" + oid.number + "?op=" + operation_name
        return requests.post(url=url, data={}, headers=self.headers)

    def query_definition(self, asset_type=""):
        url = self.urls["meta"] + "/" + asset_type
        return requests.get(url=url, headers=self.headers)

    def get_activity_stream(self, oid_token):
        url = self.urls["activity_stream"] + "/" + oid_token
        return requests.get(url=url, headers=self.headers)


def transform_data_to_asset(asset_data):
    return {
        "Attributes": reduce_asset_data(asset_data)
    }


def reduce_asset_data(dict_of_attributes):
    attributes = {}
    for key, value in dict_of_attributes.iteritems():
        if isinstance(value, list):
            attributes[key] = {
                "name": key,
                "value": [reduce_relational_attributes(related_asset) for related_asset in value]
            }
        else:
            attributes[key] = {
                "value": value,
                "act": "set"
            }
    return attributes


def reduce_relational_attributes(related_asset):
    if isinstance(related_asset, basestring):
        return {
            "idref": related_asset,
            "act": "add"
        }
    else:
        return {
            "idref": related_asset["idref"],
            "act": related_asset["act"] if related_asset.has_key("act") else "add"
        }


def get_v1_urls(hostname, instance, protocol, port):
    root_url = get_root_url(hostname, instance, protocol, port)
    return {
        "rest": root_url + "/rest-1.v1/Data",
        "query": root_url + "/query.v1",
        "meta": root_url + "/meta.v1",
        "activity_stream": root_url + "/api/ActivityStream"
    }


def get_root_url(hostname, instance, protocol, port):
    return protocol + "://" + hostname + ":" + port + instance


def create_header_objects(token, is_basic):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": ("Basic" if is_basic else "Bearer") + " " + token
    }