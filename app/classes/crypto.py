from app import db


class Transactions(db.Model):
    __tablename__ = 'transactions'
    __bind_key__ = 'shipbit'
    __table_args__ = {"schema": "public"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blockheight = db.Column(db.Integer)
    address = db.Column(db.TEXT)

    txid = db.Column(db.TEXT)
    confirmations = db.Column(db.Integer)

    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_bch = db.Column(db.DECIMAL(20, 8))