from app import app, db
from peewee import *

class Subgroup(db.Model):
	"""Subgroups currently only store query and related metadata (name of query) such
	as "tea-party republicans" or "house rules subcomittee", in the future, this class
	will define a subset of congresspeople from our database of congresspeople, and that
	is how we will determine mutual exclusivity among other things.
	"""

	id = PrimaryKeyField(null=True) #, db_column='id'
	name = CharField(null=True)
	query = TextField(null=True)
	party = CharField(null=True)
	states = TextField(null=True)
	#Later break up query into "state, party, ...." - basically
	#all of the filters that created this query.

	def is_member(congressperson):
		"""Figures out if congressperson is part of this subgroup."""
		pass

	def mutually_exclusive(subgroup):
		"""Figures out if other subgroup is mutually exclusive with this one"""
		pass

	def get_members():
		"""Returns all congresspeople that are members of this subgroup"""
		pass