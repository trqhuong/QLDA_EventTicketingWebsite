from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Time, Date
from enum import Enum as RoleEnum
from enum import Enum as ReviewEnum
from enum import Enum as TicketEnum
from enum import Enum as TypeEnum
from enum import Enum as EventEnum
from enum import Enum as MyTicketEnum
from app import db, app
from sqlalchemy.orm import relationship
from datetime import time, date, datetime
import hashlib

class Role(RoleEnum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    ORGANIZER="Organizer"

class ReviewStatus(ReviewEnum):
    PENDING_APPROVAL ="Chờ xét duyệt"
    APPROVED ="Đã duyệt"
    REJECTED="Bị từ chối"

class TicketStatus(TicketEnum):
    Available="Còn vé"
    Sold_out = "Hết vé"

class TypeTicket(TypeEnum):
    Standard ="Vé tiêu chuẩn"
    VIP="VIP"

class MyTicket_Status(MyTicketEnum):
    Unused = "Chưa sử dụng"
    Used = "Đã sử dụng"
    Cancelled = "Đã hủy"
    Expired = "Hết hạn"


class EventType(EventEnum):
    Music="Music"
    StageAndArts="StageAndArts"
    Others="Others"


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

class User(Base,  UserMixin):
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=True)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(10), nullable=True, unique=True)
    role = Column(Enum(Role), default=Role.CUSTOMER)
    organizer = relationship("Organizer",  back_populates="user", uselist=False)
    bill = relationship('Bill', backref='user', lazy=True)


class Organizer (Base):
    CompanyName = Column(String(50), nullable=False)
    TaxCode = Column(String(50), nullable=False)
    Status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING_APPROVAL)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User",  back_populates="organizer", uselist=False )
    event =relationship('Event', backref='organizer', lazy=True)

class Location(Base):
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    street= Column(String(100), nullable=False)
    event=relationship('Event', backref='location', lazy=True)

class Event(Base):
    name = Column(String(50), nullable=False)
    Time = Column(Time, nullable=False,default=lambda: time(0, 0, 0))
    Date = Column(Date, nullable=False)
    Description= Column(String(100), nullable=True)
    Type=Column(Enum(EventType), nullable=False, default=EventType.Others)
    organizer_id= Column(Integer, ForeignKey("organizer.id"))
    ticket=relationship('Ticket', backref='event', lazy=True)
    location_id= Column(Integer, ForeignKey("location.id"))


class Ticket(Base):
    Status=Column(Enum(TicketStatus), nullable=False, default=TicketStatus.Available)
    Type =Column(Enum(TypeTicket), nullable=False, default=TypeTicket.Standard)
    Price = Column(Float, nullable=False)
    Quantity = Column(Integer, nullable=False)
    event_id=Column(Integer, ForeignKey("event.id"))
    bills = relationship("Bill_Detail", back_populates="ticket")


class Bill(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    # ticket_id=Column(Integer, ForeignKey("ticket.id"))
    Status_ticket= Column(Enum(MyTicket_Status),nullable=False,default=MyTicket_Status.Unused)
    Created_date= Column(DateTime, nullable=False, default=datetime.now())
    # Ticket_quantity= Column(Integer, nullable=False)
    Total_price = Column(Float, nullable=False)
    Status_payment = Column(Boolean, nullable=False)
    tickets = relationship("Bill_Detail", back_populates="bill")

class Bill_Detail(Base):
    bill_id=Column(Integer, ForeignKey("bill.id"))
    ticket_id=Column(Integer, ForeignKey("ticket.id"))
    bought_quantity = Column(Integer, nullable=False)

    bill = relationship("Bill", back_populates="tickets")
    ticket = relationship("Ticket", back_populates="bills")


class Artist(Base):
    name = Column(String(50), nullable=False)


class Event_Artist(Base):
    artist_id=Column(Integer, ForeignKey("artist.id"))
    event_id = Column(Integer, ForeignKey("event.id"))



if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        # db.create_all()
        #
        # # --- User ---
        # admin = User(
        #     username="huong",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="admin@gmail.com",
        #     phone="0900000001",
        #     role=Role.ADMIN
        # )
        #
        # customer1 = User(
        #     username="han312",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="trantronghan@gmail.com",
        #     phone="0900000002",
        #     role=Role.CUSTOMER
        # )
        # customer2 = User(
        #     username="huong312",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="quynhhuongtran@gmail.com",
        #     phone="0900000007",
        #     role=Role.CUSTOMER
        # )
        #
        # organizer1_user = User(
        #     username="congtyA",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="lehuuhau1231@gmail.com",
        #     phone="0900000123",
        #     role=Role.ORGANIZER
        # )
        # organizer2_user = User(
        #     username="congtyB",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="lehuuhau@gmail.com",
        #     phone="0900000124",
        #     role=Role.ORGANIZER
        # )
        # organizer3_user = User(
        #     username="congtyC",
        #     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #     email="trantronghan123@gmail.com",
        #     phone="0900000145",
        #     role=Role.ORGANIZER
        # )
        #
        # db.session.add_all([admin, customer1, customer2 ,organizer1_user,organizer2_user,organizer3_user])
        # db.session.commit()
        #
        # # --- Organizer ---
        # organizer1 = Organizer(
        #     CompanyName="ABC Event Company",
        #     TaxCode="123456789",
        #     Status=ReviewStatus.APPROVED,
        #     user_id=organizer1_user.id
        # )
        # organizer2 = Organizer(
        #     CompanyName="456 Event Company",
        #     TaxCode="123456952",
        #     Status=ReviewStatus.APPROVED,
        #     user_id=organizer2_user.id
        # )
        # organizer3 = Organizer(
        #     CompanyName="ABC Company",
        #     TaxCode="123456896",
        #     Status=ReviewStatus.PENDING_APPROVAL,
        #     user_id=organizer3_user.id
        # )
        # db.session.add_all([organizer1,  organizer2, organizer3])
        # db.session.commit()
        #
        # #------location------
        # location1 = Location(city="TP.Hồ Chí Minh", district="Quận 1", street="123 Đồng Khởi")
        # location2 = Location(city="TP.Hồ Chí Minh", district="Quận 1", street="123 Nguyễn Huệ")
        # location3 = Location(city="TP.Hồ Chí Minh", district="Quận 3", street="123 Điện Biên Phủ")
        # location4 = Location(city="Hà Nội", district="Hoàn Kiếm", street="123 Bạch Đằng")
        # location5 = Location(city="Hà Nội", district="Cầu Giấy", street="123 Lê Văn Lương")
        #
        # db.session.add_all([location1, location2, location3, location4, location5])
        # db.session.commit()
        #
        # #------Event-------
        # event1 = Event(
        #     name="Concert Anh trai vượt ngàn chông gai",
        #     Time=time(17, 0),
        #     Date=date(2025, 9, 15),
        #     Description="Đỉnh nóc kịch trần bay phấp phới",
        #     Type=EventType.Music,
        #     organizer_id=1,
        #     location_id=1
        # )
        #
        # event2 = Event(
        #     name="Concert Anh trai SAY HI",
        #     Time=time(18, 0),
        #     Date=date(2025, 10, 10),
        #     Type=EventType.Music,
        #     organizer_id=2,
        #     location_id=2
        # )
        #
        # event3 = Event(
        #     name="Kí ức Hội An",
        #     Time=time(18, 10),
        #     Date=date(2025, 9, 23),
        #     Description="Thể hiện vẽ đẹp cổ xưa của Hội An",
        #     Type=EventType.StageAndArts,
        #     organizer_id=2,
        #     location_id=3
        # )
        #
        # event4 = Event(
        #     name="Conan movie 27",
        #     Time=time(14, 0),
        #     Date=date(2025, 9, 20),
        #     Description="Kịnh tính, sống động",
        #     Type=EventType.Others,
        #     organizer_id=1,
        #     location_id=4
        # )
        #
        # event5 = Event(
        #     name="Xóm trọ lắm trò",
        #     Time=time(15, 0),
        #     Date=date(2025, 10, 10),
        #     Description="Hài hước, vui nhộn",
        #     Type=EventType.StageAndArts,
        #     organizer_id=2,
        #     location_id=5
        # )
        #
        # event6 = Event(
        #     name="Thứ 4 vui vẻ",
        #     Time=time(19, 0),
        #     Date=date(2025, 10, 1),
        #     Description="Ngày xửa ngày xưa",
        #     Type=EventType.StageAndArts,
        #     organizer_id=1,
        #     location_id=4
        # )
        #
        # event7 = Event(
        #     name="Doremon và Cuộc phiêu lưu vào thế giới trong tranh",
        #     Time=time(14, 30),
        #     Date=date(2025, 9, 10),
        #     Description="Hành trình mới của doremon và nobita cũng nhóm bạn",
        #     Type=EventType.Others,
        #     organizer_id=1,
        #     location_id=1
        # )
        #
        # event8 = Event(
        #     name="Yêu nhầm bạn thân",
        #     Time=time(20, 0),
        #     Date=date(2025, 11, 1),
        #     Type=EventType.Others,
        #     organizer_id=2,
        #     location_id=2
        # )
        #
        # event9 = Event(
        #     name="Triển lãm quốc tế thể thao và giải trí ngoài trời",
        #     Time=time(9, 0),
        #     Date=date(2025, 9, 10),
        #     Type=EventType.Others,
        #     organizer_id=2,
        #     location_id=3
        # )
        #
        # db.session.add_all([event1, event2, event3, event4, event5, event6, event7, event8, event9])
        # db.session.commit()
        #
        # # --- Ticket ---
        # ticket1 = Ticket(
        #     Status=TicketStatus.Available,
        #     Type=TypeTicket.Standard,
        #     Price=500000,
        #     Quantity=100,
        #     event_id=event1.id
        # )
        #
        # ticket2 = Ticket(
        #     Status=TicketStatus.Available,
        #     Type=TypeTicket.VIP,
        #     Price=1500000,
        #     Quantity=50,
        #     event_id=event1.id
        # )
        # ticket3 = Ticket(
        #     Status=TicketStatus.Available,
        #     Type=TypeTicket.Standard,
        #     Price=400000,
        #     Quantity=100,
        #     event_id=event2.id
        # )
        #
        # ticket4 = Ticket(
        #     Status=TicketStatus.Sold_out,
        #     Type=TypeTicket.VIP,
        #     Price=1200000,
        #     Quantity=5,
        #     event_id=event2.id
        # )
        # db.session.add_all([ticket1, ticket2, ticket3, ticket4])
        # db.session.commit()
        #
        #------Bill_Detail------
        bill_detail1=Bill_Detail(bill_id=1,ticket_id=1,bought_quantity=2)
        bill_detail2=Bill_Detail(bill_id=1, ticket_id=2,bought_quantity=1)
        bill_detail3=Bill_Detail(bill_id=2, ticket_id=1,bought_quantity=3)

        db.session.add_all([bill_detail1, bill_detail2, bill_detail3])
        db.session.commit()

        # # --- Bill ---
        # bill1 = Bill(
        #     user_id=customer1.id,
        #     # ticket_id=ticket1.id,
        #     Status_ticket=MyTicket_Status.Unused,
        #     Created_date=datetime.now(),
        #     # Ticket_quantity=2,
        #     Total_price=2500000,
        #     Status_payment=True
        # )
        #
        # bill2 = Bill(
        #     user_id=customer2.id,
        #     # ticket_id=ticket2.id,
        #     Status_ticket=MyTicket_Status.Unused,
        #     Created_date=datetime.now(),
        #     # Ticket_quantity=1,
        #     Total_price=4500000,
        #     Status_payment=True
        # )
        #
        # db.session.add_all([bill1, bill2])
        # db.session.commit()
        #
        #
        # # --- Artist ---
        # artist1 = Artist(name="HieuThu2")
        # artist2 = Artist(name="Trấn Thành")
        # artist3 = Artist(name="Hoài Linh")
        # artist4 = Artist(name="Kaity Nguyễn")
        #
        # db.session.add_all([artist1, artist2, artist3, artist4])
        # db.session.commit()
        #
        # # --- Event_Artist ---
        # ea1 = Event_Artist(artist_id=artist1.id, event_id=event1.id)
        # ea2 = Event_Artist(artist_id=artist2.id, event_id=event1.id)
        # ea3 = Event_Artist(artist_id=artist3.id, event_id=event5.id)
        # ea4 = Event_Artist(artist_id=artist4.id, event_id=event8.id)
        #
        # db.session.add_all([ea1, ea2, ea3, ea4])
        # db.session.commit()
