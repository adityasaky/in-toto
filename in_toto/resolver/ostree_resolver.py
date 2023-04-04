# Copyright New York University and the in-toto contributors
# SPDX-License-Identifier: Apache-2.0

"""
<Program Name>
  ostree_resolver.py

<Author>
  Aditya Sirish A Yelgundhalli <aditya.sirish@nyu.edu>

<Started>
  April 4, 2023

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Provide resolver implementation for OSTree commits.

<Classes>
  OSTreeResolver:
      Resolver implementation for OSTree

"""

from in_toto.resolver.resolver import Resolver

class OSTreeResolver(Resolver):
  """Resolver for OSTree commits."""

  @classmethod
  def resolve_uri_to_uris(cls, generic_uri, exclude_patterns=None):
    # In OSTree, the generic_uri always to be taken at face value. It
    # represents the OSTree ref to be used. The HEAD of that ref is the hash
    # value.
    return [generic_uri]

  @classmethod
  def get_hashable_representation(cls, resolved_uri):
    # Read from the repository object store and return the object bytes.
    return b""

  @classmethod
  def hash_artifact(cls, resolved_uri):
    # Read the refs/ path to identify the hash and return it.
    # This is an example where we don't need to use
    # get_hashable_representation.
    return {}
