import securesystemslib
import unittest

from in_toto.models.statement import Statement

class TestStatementValidators(unittest.TestCase):
  """Test Statement validators."""

  def test_validate_type(self):
    statement = Statement(predicateType="none-yet")  # FIXME: none-yet
    statement.validate()

    statement._type = "bad-statement-type"
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      statement.validate()

  def test_validate_subject(self):
    statement = Statement(subject=[
      {
        "name": "artifact-path",
        "digest": {
          "sha256": "abcdef001234"
        }
      }
    ], predicateType="none-yet")  # FIXME: none-yet
    statement.validate()

    statement.subject[0]["name"] = 123
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      statement.validate()

    statement.subject[0]["name"] = "artifact-path"
    statement.subject[0]["digest"] = {
      "sha256": "qwertyuio"
    }
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      statement.validate()

    statement.subject = {
      statement.subject[0]["name"]: statement.subject[0]["digest"]
    }
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      statement.validate()

  def test_validate_predicate_type(self):
    statement = Statement(predicateType="none-yet")  # FIXME: none-yet
    statement.validate()

    statement.predicateType = 123
    with self.assertRaises(securesystemslib.exceptions.FormatError):
      statement.validate()

  def test_validate_predicate(self):
    pass  # TODO: after some predicates are implemented?
