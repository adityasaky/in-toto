import securesystemslib.hash
import securesystemslib.formats
from urllib3.util import Url
from urllib3 import PoolManager
import json


# gets github:org/repo:pr:number
# gets github:org/repo:commit:id
def _get_resolvable_url(generic_uri):
  generic_uri_split = generic_uri.split(':')

  if generic_uri_split[2] == 'pr':
    path = 'repos/{}/pulls/{}'.format(generic_uri_split[1], generic_uri_split[3])
  elif generic_uri_split[2] == 'commit':
    path = 'repos/{}/git/commits/{}'.format(generic_uri_split[1], generic_uri_split[3])

  resolvable_url = Url(scheme='https', host='api.github.com', path=path)

  return resolvable_url


def _identify_github_entity(generic_uri):
  return generic_uri.split(':')[2]


def _hash_artifact(data, hash_algorithms):
  hash_object = {}

  for algorithm in hash_algorithms:
    digest_object = securesystemslib.hash.digest(algorithm=algorithm)
    digest_object.update(securesystemslib.formats.encode_canonical(data).encode('utf-8'))
    hash_object[algorithm] = digest_object.hexdigest()

  return hash_object


def hash_artifacts(generic_uri, hash_algorithms=['sha256']):
  artifacts_dict = {}

  hashable_representation = get_hashable_representation(generic_uri)

  artifacts_dict[generic_uri] = _hash_artifact(hashable_representation, hash_algorithms)

  return artifacts_dict


def resolve_uri(generic_uri):
  return


def get_hashable_representation(generic_uri):
  resolvable_url = _get_resolvable_url(generic_uri)
  github_entity_type = _identify_github_entity(generic_uri)

  representation_object = {}

  representation_object['type'] = github_entity_type

  http = PoolManager()

  if github_entity_type == 'pr':
    response = http.request('GET', str(resolvable_url), headers={'User-Agent': 'in-toto Reference Implementation'})
    response_data = json.loads(response.data)
    commits_count = response_data['commits']
    representation_object['total_commits'] = commits_count
    representation_object['user'] = response_data['user']['login']
    representation_object['merge_commit_id'] = response_data['merge_commit_sha']

    pages = commits_count // 30  # github pagination
    if commits_count % 30 != 0:
      pages += 1

    response = http.request('GET', response_data['commits_url'] + '?page={}'.format(pages), headers={'User-Agent': 'in-toto Reference Implementation'})
    last_commit_id = json.loads(response.data)[-1]['sha']
    representation_object['commit_id'] = last_commit_id

  elif github_entity_type == 'commit':
    response = http.request('GET', str(resolvable_url), headers={'User-Agent': 'in-toto Reference Implementation'})
    response_data = json.loads(response.data)
    representation_object['commit_id'] = response_data['sha']  # we already have this without a network call...
    representation_object['parents'] = []
    for parent in response_data['parents']:
      representation_object['parents'].append(parent['sha'])
    representation_object['author'] = response_data['author']
    representation_object['committer'] = response_data['committer']
    representation_object['message'] = response_data['message']

  return representation_object

