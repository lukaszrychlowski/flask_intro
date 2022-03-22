from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
   
    def tearDown(self):
       db.session.remove()
       db.drop_all()

    def test_passwprd_hashing(self):
        u = User(username='ryszardzik')
        u.set_password('ryszard')
        self.assertFalse(u.check_password('kuna'))
        self.assertTrue(u.check_password('ryszard'))

    def test_follow(self):
        u1 = User(username='ryszardzik', email='ryszardzik@ryszard')
        u2 = User(username='ryszard', email='ryszard@ryszard')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'ryszard')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'ryszardzik')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        u1 = User(username="username1", email='username1@username')
        u2 = User(username='username2', email='username2@username')
        u3 = User(username='username3', email='username3@username')
        u4 = User(username='username4', email='username4@username')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(body='username1 post', author=u1, timestamp=now+timedelta(seconds=1))
        p2 = Post(body='username2 post', author=u2, timestamp=now+timedelta(seconds=4))
        p3 = Post(body='username3 post', author=u3, timestamp=now+timedelta(seconds=3))
        p4 = Post(body='username4 post', author=u4, timestamp=now+timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)