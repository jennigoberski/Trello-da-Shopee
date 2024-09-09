from flask_login import UserMixin
from sqlalchemy import func

from extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    boards = db.relationship('Board', secondary='membership', back_populates='members')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Board(db.Model):
    __tablename__ = 'board'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref='created_boards')
    members = db.relationship('User', secondary='membership', back_populates='boards')
    columns = db.relationship('Column', back_populates='board', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Board {self.name}>'


class Column(db.Model):
    __tablename__ = 'column'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    board = db.relationship('Board', back_populates='columns')

    order = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Column {self.name}>'


class Membership(db.Model):
    __tablename__ = 'membership'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), primary_key=True)

    approved = db.Column(db.Boolean, default=False)

    requested_at = db.Column(db.DateTime, default=db.func.now())

    approved_at = db.Column(db.DateTime, nullable=True)

    role = db.Column(db.String(50), nullable=False, default='member')

    user = db.relationship('User', backref=db.backref('memberships', cascade='all, delete-orphan'))
    board = db.relationship('Board', backref=db.backref('memberships', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Membership user_id={self.user_id}, board_id={self.board_id}, approved={self.approved}, role={self.role}>'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    column_id = db.Column(db.Integer, db.ForeignKey('column.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_cards')
    assignee = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_cards')
    board = db.relationship('Board', backref='cards')

    def __repr__(self):
        return f'<Card {self.title}>'


class JoinNotification(db.Model):
    __tablename__ = 'join_notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    board_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # New column for board owner
    created_at = db.Column(db.DateTime, default=func.now())
    approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    refused = db.Column(db.Boolean, default=False)

    user = db.relationship('User', foreign_keys=[user_id], backref='join_notifications')
    board = db.relationship('Board', backref='join_notifications')
    board_owner = db.relationship('User', foreign_keys=[board_owner_id], backref='owned_notifications')

    def __repr__(self):
        return (f'<JoinNotification id={self.id}, user_id={self.user_id}, board_id={self.board_id}, '
                f'board_owner_id={self.board_owner_id}, approved={self.approved}>')
