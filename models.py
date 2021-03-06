from google.appengine.ext import ndb
import random

class Link(ndb.Model):
    user = ndb.UserProperty()
    url = ndb.StringProperty()
    custom_path = ndb.StringProperty()
    count = ndb.IntegerProperty(default=0)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Header(ndb.Model):
    Key = ndb.StringProperty()
    Value = ndb.StringProperty()

class Counter(ndb.Model):
    count = ndb.IntegerProperty()

    @staticmethod
    @ndb.transactional()
    def increment(shard='counter'):
        """Increment the value for a given sharded counter."""
        counter = Counter.get_by_id(shard)
        if counter is None:
            counter = Counter(id=shard, count=0)
        counter.count += 1
        counter.put()

        return counter.count


class LinkExpand(ndb.Model):
    code = ndb.StringProperty()
    ip_address = ndb.StringProperty()
    header = ndb.StructuredProperty(Header, repeated=True)
    timestamp = ndb.DateTimeProperty()
