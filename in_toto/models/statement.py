# Copyright New York University and the in-toto contributors
# SPDX-License-Identifier: Apache-2.0

"""
<Program Name>
  statement.py

<Author>
  Aditya Sirish A Yelgundhalli <aditya.sirish@nyu.edu>

<Started>
  Dec 22, 2022

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Provides models for in-toto attestations.

"""

import attr
import securesystemslib

from in_toto.models.common import Signable

STATEMENT_VERSION = "v0.1"

@attr.s(repr=False, init=False)
class Statement(Signable):
  _type = attr.ib()
  subject = attr.ib()
  predicateType = attr.ib()
  predicate = attr.ib()

  def __init__(self, **kwargs):
    self._type = "https://in-toto.io/Statement/{}".format(STATEMENT_VERSION)
    self.subject = kwargs.get("subject", [])
    self.predicateType = kwargs.get("predicateType")
    self.predicate = kwargs.get("predicate")

  @property
  def type_(self):
    return self._type

  @staticmethod
  def read(data):
    # TODO: incorporate predicates
    return Statement(**data)

  def _validate_type(self):
    if self._type != \
        "https://in-toto.io/Statement/{}".format(STATEMENT_VERSION):
      raise securesystemslib.exceptions.FormatError(
          "Invalid Statement: field `_type` must be set to 'link', got: {}"
          .format(self._type))

  def _validate_subject(self):
    if not isinstance(self.subject, list):
      raise securesystemslib.exceptions.FormatError(
          "Invalid Statement: field `subject` must be of type list, got: {}"
          .format(type(self.subject)))

    for s in self.subject:
      if not isinstance(s, dict):
        raise securesystemslib.exceptions.FormatError(
          "Invalid Statement subject: expected dict, got: {}".format(type(s)))

      if "name" not in s:
        raise securesystemslib.exceptions.FormatError(
          "Invalid Statement subject: no name found for entry")

      if "digest" not in s:
        raise securesystemslib.exceptions.FormatError(
          "Invalid Statement subject: no digest found for entry {}"
          .format(s["name"]))

      securesystemslib.formats.NAME_SCHEMA.check_match(s["name"])
      securesystemslib.formats.HASHDICT_SCHEMA.check_match(s["digest"])

  def _validate_predicate_type(self):
    if not isinstance(self.predicateType, str):
      raise securesystemslib.exceptions.FormatError(
          "Invalid Statement: field `predicateType` must be a string, got: {}"
          .format(type(self.predicateType)))

  def _validate_predicate(self):
    # TODO: validate type from list of supported predicates

    # TODO: self.predicate.validate()
    pass
