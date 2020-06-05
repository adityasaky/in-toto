import securesystemslib.hash
import securesystemslib.formats
from urllib3.util import Url
from urllib3 import PoolManager
import json

# FIXME: includes some redundant network calls, possibly better to have a global dict for response data


# gets github:org/repo:pr:number
# gets github:org/repo:commit:id
# gets github:org/repo:release:tag
# gets github:org/repo:asset:id
def _get_resolvable_url(generic_uri):
  generic_uri_split = generic_uri.split(':')

  if generic_uri_split[2] == 'pr':
    path = 'repos/{}/pulls/{}'.format(generic_uri_split[1], generic_uri_split[3])
  elif generic_uri_split[2] == 'commit':
    path = 'repos/{}/git/commits/{}'.format(generic_uri_split[1], generic_uri_split[3])
  elif generic_uri_split[2] == 'release':
    path = 'repos/{}/releases/tags/{}'.format(generic_uri_split[1], generic_uri_split[3])
  elif generic_uri_split[2] == 'asset':
    path = 'repos/{}/releases/assets/{}'.format(generic_uri_split[1], generic_uri_split[3])

  # FIXME possible that .format() can be performed in the Url() call if it's consistent

  resolvable_url = Url(scheme='https', host='api.github.com', path=path)

  return resolvable_url


def _identify_github_entity(generic_uri):
  return generic_uri.split(':')[2]


def _hash_artifact(data, hash_algorithms):
  hash_object = {}

  for algorithm in hash_algorithms:
    digest_object = securesystemslib.hash.digest(algorithm=algorithm)
    if isinstance(data, dict):
      digest_object.update(securesystemslib.formats.encode_canonical(data).encode('utf-8'))
    elif isinstance(data, bytes):
      digest_object.update(data)
    hash_object[algorithm] = digest_object.hexdigest()

  return hash_object


def hash_artifacts(generic_uri, hash_algorithms=['sha256']):
  artifacts_dict = {}

  all_uris = []

  if _identify_github_entity(generic_uri) == 'release':
    all_uris = resolve_uri(generic_uri) # decide if this is going to return with generic_uri also in it for the release artifact
  else:
    all_uris.append(generic_uri)

  for uri in all_uris:
    hashable_representation = get_hashable_representation(uri)
    if _identify_github_entity(uri) == 'asset':
      artifacts_dict[hashable_representation['uri_to_use']] = _hash_artifact(hashable_representation['data'], hash_algorithms)
    else:
      artifacts_dict[uri] = _hash_artifact(hashable_representation, hash_algorithms)

  return artifacts_dict


def resolve_uri(generic_uri):
  all_uris = []

  all_uris.append(generic_uri)

  resolvable_url = _get_resolvable_url(generic_uri)

  http = PoolManager()

  response = http.request('GET', str(resolvable_url), headers={'User-Agent': 'in-toto Reference Implementation'})
  response_data = json.loads(response.data)

  for asset in response_data['assets']:
    all_uris.append('github:{}:asset:{}'.format(generic_uri.split(':')[1], asset['id']))

  return all_uris


def get_hashable_representation(generic_uri):
  resolvable_url = _get_resolvable_url(generic_uri)
  github_entity_type = _identify_github_entity(generic_uri)

  http = PoolManager()

  response = http.request('GET', str(resolvable_url), headers={'User-Agent': 'in-toto Reference Implementation'})
  response_data = json.loads(response.data)

  representation_object = {}

  representation_object['type'] = github_entity_type

  if github_entity_type == 'pr':
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
    representation_object['commit_id'] = response_data['sha']  # we already have this without a network call...
    representation_object['parents'] = []
    for parent in response_data['parents']:
      representation_object['parents'].append(parent['sha'])
    representation_object['author'] = response_data['author']
    representation_object['committer'] = response_data['committer']
    representation_object['message'] = response_data['message']

  elif github_entity_type == 'release':
    # first, the idea is we have hashes for the materials that were uploaded
    # when drafting the new release. Taking in-toto/in-toto as an example, these
    # would be the archive and wheel (and the corresponding signature files).
    # next, when the release is actually passed in as an artifact, we create
    # an entity for the release as a whole - hash a hashable representation -
    # and loop over the assets, download the attached assets, and calculate
    # their hashes

    representation_object['release_id'] = response_data['id']
    representation_object['tag'] = response_data['tag_name']
    representation_object['draft_status'] = response_data['draft']
    representation_object['author'] = response_data['author']['login']
    representation_object['created_at'] = response_data['created_at']
    representation_object['published_at'] = response_data['published_at']

  elif github_entity_type == 'asset':
    # fetches the asset API response to get the downloadable link
    # then calculates hash over the bytes in-memory; potential FIXME

    download_url = response_data['browser_download_url']

    response = http.request('GET', download_url, headers={'User-Agent': 'in-toto Reference Implementation'})

    representation_object['uri_to_use'] = response_data['name']
    representation_object['data'] = response.data

  return representation_object

