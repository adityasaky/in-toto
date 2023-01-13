import attr

from in_toto.models.link import Link
from in_toto.models.statement import Statement

class LinkPredicate():
  name = attr.ib()
  materials = attr.ib()
  byproducts = attr.ib()
  command = attr.ib()
  environment = attr.ib()

  def __init__(self, **kwargs):
    self.name = kwargs.get("name")
    self.materials = kwargs.get("materials", {})
    self.byproducts = kwargs.get("byproducts", {})
    self.command = kwargs.get("command", [])
    self.environment = kwargs.get("environment", {})

  @property
  def type_(self):
    return "https://in-toto.io/Link/v0.2"


def convert_link_attestation_to_legacy_link(statement: Statement):
  expected_type = LinkPredicate().type_
  if statement.predicateType != expected_type:
    raise ValueError(
      f"Invalid LinkPredicate: field `predicateType` is not `{expected_type}`"
    )

  return Link(
    name=statement.predicate.name,
    materials=statement.predicate.materials,
    command=statement.predicate.command,
    products={p["name"]: p["digest"] for p in statement.subject},
    environment=statement.predicate.environment,
    byproducts=statement.predicate.byproducts
  )
