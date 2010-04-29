from redish.utils import maybe_datetime
from redish.models import Model, Manager


class Entry(Model):

    def post_save(self):
        self.guid_index.add(self.guid)
        self.sort_index.add(self.id, maybe_datetime(self.timestamp))

    def post_delete(self):
        self.guid_index.remove(self.guid)
        self.sort_index.remove(self.id)

    @property
    def guid_index(self):
        return self.objects.Set((self.feed_url, "guid"))

    @property
    def sort_index(self):
        return self.objects.SortedSet((self.feed_url, "sort"))


class Entries(Manager):
    db = "feeds"
    model = Entry


if __name__ == "__main__":
    from datetime import datetime
    posts = Entries(host="localhost")

    feed1 = dict(feed_url="http://rss.com/example",
                 title="Example Post",
                 guid="http://rss.com/example/1",
                 link="http://rss.com/example/1",
                 content="This is an example",
                 timestamp=datetime.now())
    entry = posts.Entry(**data)
    entry_id = entry.save()
    assert entry_id == entry.id

    stored = posts.get(entry_id)
    stored.content = "Content has been changed"
    entry_id = stored.save()
    assert stored.id == new_id)
    again = posts.get(entry_id)

    stored.delete()

    feed2 = posts.create(**data)

    for post in iter(posts):
        print("(%s) %s" % (post.id, post.title))
