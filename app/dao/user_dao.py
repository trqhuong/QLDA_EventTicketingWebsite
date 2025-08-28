import re
import unicodedata
from app import db
from app.models import User,Role,  Organizer, ReviewStatus
import hashlib

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.role.__eq__(role))
    return u.first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def remove_vietnamese_accents(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'\s+', '', s)
    return s

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_user_from_google(user_info):
    email = user_info["email"]
    raw_name = user_info.get("name", email.split("@")[0])
    username = remove_vietnamese_accents(raw_name)

    user = User(username=username, email=email, password=None, phone=None)
    db.session.add(user)
    db.session.commit()
    return user


def add_customer(username, password, email, phone=None, avatar=None):
    hashed_pw =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    user = User(
        username=username,
        password=hashed_pw,
        email=email,
        phone=phone,
        role=Role.CUSTOMER
    )

    db.session.add(user)
    db.session.commit()
    return user

def add_organizer(username, password, email, company_name, tax_code, phone=None):
    hashed_pw = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    # Tạo user với role ORGANIZER
    user = User(
        username=username,
        password=hashed_pw,
        email=email,
        phone=phone,
        role=Role.ORGANIZER
    )
    db.session.add(user)
    db.session.commit()  # commit để có user.id

    # Tạo organizer
    organizer = Organizer(
        CompanyName=company_name,
        TaxCode=tax_code,
        user_id=user.id,
        Status=ReviewStatus.PENDING_APPROVAL
    )
    db.session.add(organizer)
    db.session.commit()

    return user, organizer


def existence_check(table, attribute, value):
    return table.query.filter(getattr(table, attribute).__eq__(value)).first()