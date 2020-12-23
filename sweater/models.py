from datetime import datetime

from flask_login import UserMixin

from sweater import db, login_manager

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow())

    def __repr__(self):
        return '<User %r>' % self.id


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(128), nullable=False)
    cut = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow())
    
    # С владельцем отношение многие к одному
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    owner = db.relationship('User', backref=db.backref('owner', lazy=True))
    # С тэгами отношение многие ко многим
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('articles', lazy=True))
    # С комментариями отношения один ко многим
    comments = db.relationship('Comment', lazy=True,
        backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return '<Article %r>' % self.id    


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, 
        default=datetime.utcnow())

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref('creater', lazy=True))

    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    article = db.relationship('Article', backref=db.backref('article', lazy=True))

    def __repr__(self):
        return '<Comment %r' % self.id


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<tag %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)