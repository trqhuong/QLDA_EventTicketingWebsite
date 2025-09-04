from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Time, Date, text
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
    company_name = Column(String(50), nullable=False)
    tax_code = Column(String(50), nullable=False)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING_APPROVAL)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User",  back_populates="organizer", uselist=False )
    event =relationship('Event', backref='organizer', lazy=True)

class City(Base):
    name = Column(String(100), nullable=False)
    event=relationship('Event', backref='city', lazy=True)

class District(Base):
    name = Column(String(100), nullable=False)
    event = relationship('Event', backref='district', lazy=True)
    city_id = Column(Integer, ForeignKey("city.id"))

class EventType(Base):
    name = Column(String(50), nullable=False)


class Event(Base):
    name = Column(String(50), nullable=False)
    time = Column(Time, nullable=False,default=lambda: time(0, 0, 0))
    date = Column(Date, nullable=False)
    description= Column(String(500), nullable=True)
    address = Column(String(255), nullable=False)
    event_type_id= Column(Integer, ForeignKey("event_type.id"))
    event_type = relationship("EventType", backref="events", lazy=True)
    organizer_id= Column(Integer, ForeignKey("organizer.id"))
    ticket=relationship('Ticket', backref='event', lazy=True)
    city_id= Column(Integer, ForeignKey("city.id"))
    district_id = Column(Integer, ForeignKey("district.id"))
    image_url = Column(String(255), nullable=True)


class Ticket(Base):
    status=Column(Enum(TicketStatus), nullable=False, default=TicketStatus.Available)
    type =Column(Enum(TypeTicket), nullable=False, default=TypeTicket.Standard)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    event_id=Column(Integer, ForeignKey("event.id"))
    bills = relationship("Bill_Detail", back_populates="ticket")


class Bill(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    # ticket_id=Column(Integer, ForeignKey("ticket.id"))
    status_ticket= Column(Enum(MyTicket_Status),nullable=False,default=MyTicket_Status.Unused)
    created_date= Column(DateTime, nullable=False, default=datetime.now())
    # Ticket_quantity= Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status_payment = Column(Boolean, nullable=False)
    tickets = relationship("Bill_Detail", back_populates="bill")

class Bill_Detail(Base):
    bill_id=Column(Integer, ForeignKey("bill.id"))
    ticket_id=Column(Integer, ForeignKey("ticket.id"))
    bought_quantity = Column(Integer, nullable=False)

    bill = relationship("Bill", back_populates="tickets")
    ticket = relationship("Ticket", back_populates="bills")

class Artist(Base):
    name = Column(String(100), nullable=False)

class EventArtist(Base):
    artist_id = Column(Integer, ForeignKey('artist.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()

        # --- User ---
        admin = User(
            username="huong",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="admin@gmail.com",
            phone="0900000001",
            role=Role.ADMIN
        )

        customer1 = User(
            username="han312",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="trantronghan@gmail.com",
            phone="0900000002",
            role=Role.CUSTOMER
        )
        customer2 = User(
            username="huong312",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="quynhhuongtran@gmail.com",
            phone="0900000007",
            role=Role.CUSTOMER
        )

        organizer1_user = User(
            username="congtyA",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="lehuuhau1231@gmail.com",
            phone="0900000123",
            role=Role.ORGANIZER
        )
        organizer2_user = User(
            username="congtyB",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="lehuuhau@gmail.com",
            phone="0900000124",
            role=Role.ORGANIZER
        )
        organizer3_user = User(
            username="congtyC",
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            email="trantronghan123@gmail.com",
            phone="0900000145",
            role=Role.ORGANIZER
        )

        db.session.add_all([admin, customer1, customer2 ,organizer1_user,organizer2_user,organizer3_user])
        db.session.commit()

        # --- Organizer ---
        organizer1 = Organizer(
            company_name="ABC Event Company",
            tax_code="123456789",
            status=ReviewStatus.APPROVED,
            user_id=organizer1_user.id
        )
        organizer2 = Organizer(
            company_name="456 Event Company",
            tax_code="123456952",
            status=ReviewStatus.APPROVED,
            user_id=organizer2_user.id
        )
        organizer3 = Organizer(
            company_name="ABC Company",
            tax_code="123456896",
            status=ReviewStatus.PENDING_APPROVAL,
            user_id=organizer3_user.id
        )
        db.session.add_all([organizer1,  organizer2, organizer3])
        db.session.commit()

        #------location------
        city1 = City(name="TP.Hồ Chí Minh")
        city2 = City(name="Hà Nội")
        city3 = City(name="Đà Nẵng")

        db.session.add_all([city1, city2, city3])
        db.session.commit()

        district1 = District(name="Quận 1", city_id = city1.id)
        district2 = District(name="Quận 3", city_id=city1.id)
        district3 = District(name="Quận 5", city_id=city1.id)
        district4 = District(name="Quận Đống Đa", city_id=city2.id)
        district5 = District(name="Quận DN", city_id=city3.id)

        db.session.add_all([district1, district2, district3, district4, district5])
        db.session.commit()

        #------EventType------
        event_type1=EventType(name="Âm nhạc")
        event_type2=EventType(name="Sân khấu & Nghệ thuật")
        event_type3=EventType(name="Thể thao")
        event_type4=EventType(name="Hội chợ & Triển lãm")

        db.session.add_all([event_type1, event_type2, event_type3, event_type4])
        db.session.commit()

        #------Event-------
        event1 = Event(
            name="Concert Anh trai vượt ngàn chông gai",
            time=time(17, 0),
            date=date(2025, 9, 15),
            description="Đêm nhạc sôi động với sự góp mặt của nhiều nghệ sĩ nổi tiếng, mang đến những giai điệu đầy cảm xúc.",
            address="123 Nguyễn Kiệm",
            event_type_id=event_type1.id,
            organizer_id=1,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861619/1_pumfa1.png"
        )

        event2 = Event(
            name="Concert Anh trai SAY HI",
            time=time(18, 0),
            date=date(2025, 10, 10),
            description="Chương trình âm nhạc trẻ trung, hiện đại, nơi khán giả được giao lưu và hòa mình vào không khí náo nhiệt.",
            address="123 Nguyễn Du",
            event_type_id=event_type2.id,
            organizer_id=2,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861637/2_ccodpr.jpg"
        )

        event3 = Event(
            name="Kí ức Hội An",
            time=time(18, 10),
            date=date(2025, 9, 23),
            description="Chương trình tái hiện không gian văn hóa, nghệ thuật và đời sống cổ xưa đặc trưng của phố Hội.",
            address="123 Lê Lợi",
            event_type_id=event_type2.id,
            organizer_id=1,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861639/3_mbrfgz.jpg"
        )

        event4 = Event(
            name="Conan movie 27",
            time=time(14, 0),
            date=date(2025, 9, 20),
            description="Bộ phim hoạt hình trinh thám hấp dẫn với những pha hành động gay cấn và bí ẩn kịch tính.",
            address="123 Nguyễn Chi Phương",
            event_type_id=event_type3.id,
            organizer_id=1,
            city_id=city2.id,
            district_id=district4.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861740/4_dfpm8r.jpg"
        )

        event5 = Event(
            name="Xóm trọ lắm trò",
            time=time(15, 0),
            date=date(2025, 10, 10),
            description="Vở kịch hài hước phản ánh cuộc sống đời thường, mang đến những tràng cười sảng khoái cho khán giả.",
            address="123 Trần Phú",
            event_type_id=event_type1.id,
            organizer_id=1,
            city_id=city1.id,
            district_id=district3.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861749/5_mfkrih.jpg"
        )

        event6 = Event(
            name="Thứ 4 vui vẻ",
            time=time(19, 0),
            date=date(2025, 10, 1),
            description="Chương trình giải trí tổng hợp, mang lại niềm vui và tiếng cười cho mọi lứa tuổi vào giữa tuần.",
            address="14 Nguyễn Trãi",
            event_type_id=event_type1.id,
            organizer_id=1,
            city_id=city1.id,
            district_id=district2.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861793/6_imhqme.jpg"
        )

        event7 = Event(
            name="Doremon và Cuộc phiêu lưu vào thế giới trong tranh",
            time=time(14, 30),
            date=date(2025, 9, 10),
            description="Bộ phim hoạt hình mới với hành trình kỳ thú của Doraemon, Nobita và nhóm bạn trong thế giới hội họa.",
            address="số 2 Phan Đình Phùng",
            event_type_id=event_type1.id,
            organizer_id=1,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861795/7_eae6nl.png"
        )

        event8 = Event(
            name="Yêu nhầm bạn thân",
            time=time(20, 0),
            date=date(2025, 11, 1),
            description="Bộ phim tình cảm lãng mạn, hài hước về tình bạn và tình yêu đầy trắc trở.",
            address="54 Hoàng Văn Thụ",
            event_type_id=event_type1.id,
            organizer_id=2,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861801/8_k9vu5t.jpg"
        )

        event9 = Event(
            name="Triển lãm quốc tế thể thao và giải trí ngoài trời",
            time=time(9, 0),
            date=date(2025, 9, 10),
            description="Sự kiện triển lãm quy mô lớn giới thiệu các sản phẩm, dịch vụ và hoạt động trong lĩnh vực thể thao, giải trí ngoài trời.",
            address="34 Cộng Hòa",
            event_type_id=event_type1.id,
            organizer_id=2,
            city_id=city1.id,
            district_id=district1.id,
            image_url="https://res.cloudinary.com/dfi68mgij/image/upload/v1756861806/9_y9let1.jpg"
        )

        db.session.add_all([event1, event2, event3, event4, event5, event6, event7, event8, event9])
        db.session.commit()

        artist1=Artist(name="Trần Trung Thành")
        artist2=Artist(name="Trần Quang Đạt")
        artist3=Artist(name="Trần Đình Quang")
        artist4=Artist(name="Trần Trung Hiếu")

        db.session.add_all([artist1, artist2, artist3, artist4])
        db.session.commit()

        # --- Ticket ---
        #--event1---
        ticket1 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=500000,
            quantity=100,
            event_id=event1.id
        )
        ticket2 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=1500000,
            quantity=50,
            event_id=event1.id
        )
        #---event2---
        ticket3 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=400000,
            quantity=100,
            event_id=event2.id
        )
        ticket4 = Ticket(
            status=TicketStatus.Sold_out,
            type=TypeTicket.VIP,
            price=1200000,
            quantity=5,
            event_id=event2.id
        )
        # Event 3
        ticket5 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=300000,
            quantity=150,
            event_id=event3.id
        )
        ticket6 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=800000,
            quantity=50,
            event_id=event3.id
        )

        # Event 4
        ticket7 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=100000,
            quantity=200,
            event_id=event4.id
        )
        ticket8 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=300000,
            quantity=80,
            event_id=event4.id
        )

        # Event 5
        ticket9 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=200000,
            quantity=120,
            event_id=event5.id
        )
        ticket10 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=600000,
            quantity=40,
            event_id=event5.id
        )

        # Event 6
        ticket11 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=150000,
            quantity=100,
            event_id=event6.id
        )
        ticket12 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=500000,
            quantity=30,
            event_id=event6.id
        )

        # Event 7
        ticket13 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=120000,
            quantity=150,
            event_id=event7.id
        )
        ticket14 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=400000,
            quantity=50,
            event_id=event7.id
        )

        # Event 8
        ticket15 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=80000,
            quantity=200,
            event_id=event8.id
        )
        ticket16 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=250000,
            quantity=70,
            event_id=event8.id
        )

        # Event 9
        ticket17 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.Standard,
            price=50000,
            quantity=300,
            event_id=event9.id
        )
        ticket18 = Ticket(
            status=TicketStatus.Available,
            type=TypeTicket.VIP,
            price=200000,
            quantity=100,
            event_id=event9.id
        )

        # Add tất cả vào DB
        db.session.add_all([
            ticket5, ticket6, ticket7, ticket8, ticket9, ticket10,
            ticket11, ticket12, ticket13, ticket14, ticket15, ticket16,
            ticket17, ticket18
        ])
        db.session.commit()

        # --- Bill ---
        bill1 = Bill(
            user_id=customer1.id,
            # ticket_id=ticket1.id,
            status_ticket=MyTicket_Status.Unused,
            created_date=datetime.now(),
            # Ticket_quantity=2,
            total_price=2500000,
            status_payment=True
        )

        bill2 = Bill(
            user_id=customer2.id,
            # ticket_id=ticket2.id,
            status_ticket=MyTicket_Status.Unused,
            created_date=datetime.now(),
            # Ticket_quantity=1,
            total_price=4500000,
            status_payment=True
        )

        db.session.add_all([bill1, bill2])
        db.session.commit()
        #
        #------Bill_Detail------
        bill_detail1=Bill_Detail(bill_id=1,ticket_id=1,bought_quantity=2)
        bill_detail2=Bill_Detail(bill_id=1, ticket_id=2,bought_quantity=1)
        bill_detail3=Bill_Detail(bill_id=2, ticket_id=1,bought_quantity=3)

        db.session.add_all([bill_detail1, bill_detail2, bill_detail3])
        db.session.commit()
