import json
from jsonpath_ng import parse
import securesystemslib.hash


SEPARATOR = '.'
SELECTOR = '$'
JSONPATH_RESERVED = ['.', '$', '+', '?', ':']


def _hash_artifact(data, hash_algorithms):
  hash_object = {}

  for algorithm in hash_algorithms:
    digest_object = securesystemslib.hash.digest(algorithm=algorithm)
    digest_object.update(str(data).encode('utf-8'))
    hash_object[algorithm] = digest_object.hexdigest()

  return hash_object


def hash_artifacts(generic_uri, hash_algorithms=['sha256']):
  artifacts_dict = {}
  actual_file = generic_uri.split('cnab+json:')[1]

  with open(actual_file) as fp:
    bundle = json.load(fp)

  all_uris = resolve_uri(generic_uri, bundle)

  for uri in all_uris:
    artifacts_dict[uri] = _hash_artifact(get_hashable_representation(uri, bundle), hash_algorithms)

  return artifacts_dict


def _flatten(dictionary, parent_key='', separator=SEPARATOR):
  all_uris = []
  for key, value in dictionary.items():
    if len(set(JSONPATH_RESERVED) & set(list(key))):
      key = '["' + key + '"]'
    new_key = parent_key + separator + key if parent_key else key
    # uncomment line below to record intermediate dictionaries, comment out else below
    # all_uris.append(new_key)
    if isinstance(value, dict):
      all_uris.extend(_flatten(value, new_key))
    elif isinstance(value, list) and isinstance(value[0], dict):  # hacky af
      # assumes all values in the list are dicts...
      for i in range(len(value)):
        all_uris.extend(_flatten(value[i],
                        new_key + SEPARATOR + '[' + str(i) + ']'))
    else:
      all_uris.append(new_key)  # only record leaves
  return all_uris


def resolve_uri(generic_uri, bundle):
  all_uris = _flatten(bundle, parent_key=SELECTOR)
  return [generic_uri + uri for uri in all_uris]


def get_hashable_representation(generic_uri, bundle):
  key = SELECTOR + generic_uri.split(SELECTOR)[1]
  json_expression = parse(key)
  return json_expression.find(bundle)[0].value
