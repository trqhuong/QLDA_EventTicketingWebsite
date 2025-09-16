from app.models import Bill, Bill_Detail, db, MyTicket_Status, Event, Ticket, User, Organizer
from app.dao import user_dao,ticket_dao
from datetime import datetime
from app import utils
from sqlalchemy import extract, func, and_, desc, case
import uuid
import random
import string



def create_bill_bill_detail(user=  None,cart = None):
     current_user = user_dao.get_user_by_email(user.email)

     total = 0
     for key in cart:
         total += cart[key]['quantity'] * cart[key]['price']

     bill = Bill(user_id = current_user.id, status_ticket = MyTicket_Status.Unused,
                 created_date = datetime.now(),total_price = float(total), status_payment = True )
     db.session.add(bill)
     db.session.commit()

     for item in cart.values():
         ticket = ticket_dao.get_ticket_by_ticket_id(int(item['ticket_id']))
         ticket.quantity -= int(item['quantity'])
         while True:
             rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
             code = f"EVT{item['ticket_id']}-{rand_str(6)}"
             if not db.session.query(Ticket).filter_by(ticket_code=code).first():
                 break
         bill_detail = Bill_Detail(
             bill_id = bill.id,
             ticket_id = int(item['ticket_id']),
             bought_quantity = int(item['quantity']),
             code=code
         )
         db.session.add(bill_detail)
     db.session.commit()
     return bill

def get_report_data(organizer_id, year=None, month=None, quarter=None):
    """
    Lấy dữ liệu thống kê cho organizer
    """
    # Base query cho events của organizer
    events_query = Event.query.filter(Event.organizer_id == organizer_id)

    # Lọc theo năm, tháng, hoặc quý
    if year:
        events_query = events_query.filter(extract('year', Event.date) == year)
    if month:
        events_query = events_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        events_query = events_query.filter(extract('month', Event.date).in_(quarter_months))

    # Tổng số sự kiện
    total_events = events_query.count()

    # Tính tổng doanh thu
    revenue_query = db.session.query(func.sum(Bill.total_price))\
        .join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
        .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
        .join(Event, Ticket.event_id == Event.id)\
        .filter(Event.organizer_id == organizer_id)\
        .filter(Bill.status_payment == True)

    if year:
        revenue_query = revenue_query.filter(extract('year', Event.date) == year)
    if month:
        revenue_query = revenue_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        revenue_query = revenue_query.filter(extract('month', Event.date).in_(quarter_months))

    total_revenue = revenue_query.scalar() or 0

    return {
        'total_events': total_events,
        'total_revenue': total_revenue
    }

def get_quarter_months(quarter):
    """
    Trả về danh sách tháng thuộc quý được chỉ định
    """
    quarter_mapping = {
        1: [1, 2, 3],    # Quý 1
        2: [4, 5, 6],    # Quý 2
        3: [7, 8, 9],    # Quý 3
        4: [10, 11, 12]  # Quý 4
    }
    return quarter_mapping.get(quarter, [])

def get_monthly_events_data(organizer_id, year=None, month=None, quarter=None):
    """
    Lấy số lượng sự kiện theo từng tháng hoặc theo tháng/quý cụ thể
    """
    if quarter:
        # Nếu lọc theo quý, trả về dữ liệu 3 tháng của quý đó
        quarter_months = get_quarter_months(quarter)
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.count(Event.id).label('count')
        ).filter(Event.organizer_id == organizer_id)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date).in_(quarter_months))
        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 3 tháng của quý
        quarterly_data = [0] * 3
        for month_num, count in results:
            # Tính index trong quý (0, 1, 2)
            quarter_index = (int(month_num) - quarter_months[0])
            if 0 <= quarter_index < 3:
                quarterly_data[quarter_index] = count

        return quarterly_data
    elif month:
        # Nếu lọc theo tháng cụ thể, chỉ trả về dữ liệu của tháng đó
        query = db.session.query(
            func.count(Event.id).label('count')
        ).filter(Event.organizer_id == organizer_id)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date) == month)

        result = query.scalar() or 0
        return [result]  # Trả về array với 1 phần tử
    else:
        # Nếu không lọc theo tháng, trả về dữ liệu 12 tháng
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.count(Event.id).label('count')
        ).filter(Event.organizer_id == organizer_id)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 12 tháng
        monthly_data = [0] * 12
        for month_num, count in results:
            monthly_data[int(month_num) - 1] = count

        return monthly_data

def get_monthly_revenue_data(organizer_id, year=None, month=None, quarter=None):
    """
    Lấy doanh thu theo từng tháng hoặc theo tháng/quý cụ thể
    """
    if quarter:
        # Nếu lọc theo quý, trả về dữ liệu 3 tháng của quý đó
        quarter_months = get_quarter_months(quarter)
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Event.organizer_id == organizer_id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date).in_(quarter_months))
        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 3 tháng của quý
        quarterly_data = [0] * 3
        for month_num, revenue in results:
            # Tính index trong quý (0, 1, 2)
            quarter_index = (int(month_num) - quarter_months[0])
            if 0 <= quarter_index < 3:
                quarterly_data[quarter_index] = float(revenue or 0)

        return quarterly_data
    elif month:
        # Nếu lọc theo tháng cụ thể, chỉ trả về dữ liệu của tháng đó
        query = db.session.query(
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Event.organizer_id == organizer_id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date) == month)

        result = query.scalar() or 0
        return [float(result)]  # Trả về array với 1 phần tử
    else:
        # Nếu không lọc theo tháng, trả về dữ liệu 12 tháng
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Event.organizer_id == organizer_id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 12 tháng
        monthly_data = [0] * 12
        for month_num, revenue in results:
            monthly_data[int(month_num) - 1] = float(revenue or 0)

        return monthly_data

def get_available_years(organizer_id):
    """
    Lấy danh sách các năm có sự kiện của organizer
    """
    years = db.session.query(
        extract('year', Event.date).label('year')
    ).filter(Event.organizer_id == organizer_id)\
     .distinct()\
     .order_by(desc('year')).all()

    return [int(year[0]) for year in years]

def get_event_statistics(organizer_id, year=None, month=None, quarter=None):
    """
    Lấy thống kê chi tiết sự kiện
    """
    # Danh sách sự kiện với thông tin ticket đã bán
    events_query = db.session.query(
        Event.id,
        Event.name,
        Event.date,
        Event.time,
        func.coalesce(func.sum(Bill_Detail.bought_quantity), 0).label('tickets_sold'),
        func.coalesce(func.sum(Bill.total_price), 0).label('revenue')
    ).outerjoin(Ticket, Event.id == Ticket.event_id)\
     .outerjoin(Bill_Detail, Ticket.id == Bill_Detail.ticket_id)\
     .outerjoin(Bill, and_(Bill.id == Bill_Detail.bill_id, Bill.status_payment == True))\
     .filter(Event.organizer_id == organizer_id)

    if year:
        events_query = events_query.filter(extract('year', Event.date) == year)
    if month:
        events_query = events_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        events_query = events_query.filter(extract('month', Event.date).in_(quarter_months))

    events_query = events_query.group_by(Event.id, Event.name, Event.date, Event.time)\
                               .order_by(desc(Event.date))

    return events_query.all()

# ============ ADMIN FUNCTIONS (Toàn hệ thống) ============

def get_admin_report_data(year=None, month=None, quarter=None):
    """
    Lấy dữ liệu thống kê cho admin (toàn hệ thống)
    """
    # Base query cho tất cả events
    events_query = Event.query

    # Lọc theo năm, tháng, hoặc quý
    if year:
        events_query = events_query.filter(extract('year', Event.date) == year)
    if month:
        events_query = events_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        events_query = events_query.filter(extract('month', Event.date).in_(quarter_months))

    # Tổng số sự kiện
    total_events = events_query.count()

    # Tính tổng doanh thu
    revenue_query = db.session.query(func.sum(Bill.total_price))\
        .join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
        .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
        .join(Event, Ticket.event_id == Event.id)\
        .filter(Bill.status_payment == True)

    if year:
        revenue_query = revenue_query.filter(extract('year', Event.date) == year)
    if month:
        revenue_query = revenue_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        revenue_query = revenue_query.filter(extract('month', Event.date).in_(quarter_months))

    total_revenue = revenue_query.scalar() or 0

    return {
        'total_events': total_events,
        'total_revenue': total_revenue
    }

def get_admin_monthly_events_data(year=None, month=None, quarter=None):
    """
    Lấy số lượng sự kiện theo từng tháng cho admin (toàn hệ thống)
    """
    if quarter:
        # Nếu lọc theo quý, trả về dữ liệu 3 tháng của quý đó
        quarter_months = get_quarter_months(quarter)
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.count(Event.id).label('count')
        )

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date).in_(quarter_months))
        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 3 tháng của quý
        quarterly_data = [0] * 3
        for month_num, count in results:
            # Tính index trong quý (0, 1, 2)
            quarter_index = (int(month_num) - quarter_months[0])
            if 0 <= quarter_index < 3:
                quarterly_data[quarter_index] = count

        return quarterly_data
    elif month:
        # Nếu lọc theo tháng cụ thể, chỉ trả về dữ liệu của tháng đó
        query = db.session.query(
            func.count(Event.id).label('count')
        )

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date) == month)

        result = query.scalar() or 0
        return [result]  # Trả về array với 1 phần tử
    else:
        # Nếu không lọc theo tháng, trả về dữ liệu 12 tháng
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.count(Event.id).label('count')
        )

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 12 tháng
        monthly_data = [0] * 12
        for month_num, count in results:
            monthly_data[int(month_num) - 1] = count

        return monthly_data

def get_admin_monthly_revenue_data(year=None, month=None, quarter=None):
    """
    Lấy doanh thu theo từng tháng cho admin (toàn hệ thống)
    """
    if quarter:
        # Nếu lọc theo quý, trả về dữ liệu 3 tháng của quý đó
        quarter_months = get_quarter_months(quarter)
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date).in_(quarter_months))
        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 3 tháng của quý
        quarterly_data = [0] * 3
        for month_num, revenue in results:
            # Tính index trong quý (0, 1, 2)
            quarter_index = (int(month_num) - quarter_months[0])
            if 0 <= quarter_index < 3:
                quarterly_data[quarter_index] = float(revenue or 0)

        return quarterly_data
    elif month:
        # Nếu lọc theo tháng cụ thể, chỉ trả về dữ liệu của tháng đó
        query = db.session.query(
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.filter(extract('month', Event.date) == month)

        result = query.scalar() or 0
        return [float(result)]  # Trả về array với 1 phần tử
    else:
        # Nếu không lọc theo tháng, trả về dữ liệu 12 tháng
        query = db.session.query(
            extract('month', Event.date).label('month'),
            func.sum(Bill.total_price).label('revenue')
        ).join(Bill_Detail, Bill.id == Bill_Detail.bill_id)\
         .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
         .join(Event, Ticket.event_id == Event.id)\
         .filter(Bill.status_payment == True)

        if year:
            query = query.filter(extract('year', Event.date) == year)

        query = query.group_by(extract('month', Event.date))

        results = query.all()

        # Tạo array cho 12 tháng
        monthly_data = [0] * 12
        for month_num, revenue in results:
            monthly_data[int(month_num) - 1] = float(revenue or 0)

        return monthly_data

def get_admin_available_years():
    """
    Lấy danh sách các năm có sự kiện trong toàn hệ thống
    """
    years = db.session.query(
        extract('year', Event.date).label('year')
    ).distinct()\
     .order_by(desc('year')).all()

    return [int(year[0]) for year in years]

def get_admin_event_statistics(year=None, month=None, quarter=None):
    """
    Lấy thống kê chi tiết sự kiện cho admin (toàn hệ thống)
    """
    # Danh sách sự kiện với thông tin ticket đã bán
    events_query = db.session.query(
        Event.id,
        Event.name,
        Event.date,
        Event.time,
        Organizer.company_name,
        func.coalesce(func.sum(Bill_Detail.bought_quantity), 0).label('tickets_sold'),
        func.coalesce(func.sum(Bill.total_price), 0).label('revenue')
    ).outerjoin(Ticket, Event.id == Ticket.event_id)\
     .outerjoin(Bill_Detail, Ticket.id == Bill_Detail.ticket_id)\
     .outerjoin(Bill, and_(Bill.id == Bill_Detail.bill_id, Bill.status_payment == True))\
     .join(Organizer, Event.organizer_id == Organizer.id)

    if year:
        events_query = events_query.filter(extract('year', Event.date) == year)
    if month:
        events_query = events_query.filter(extract('month', Event.date) == month)
    if quarter:
        quarter_months = get_quarter_months(quarter)
        events_query = events_query.filter(extract('month', Event.date).in_(quarter_months))

    events_query = events_query.group_by(Event.id, Event.name, Event.date, Event.time, Organizer.company_name)\
                               .order_by(desc(Event.date))

    return events_query.all()

def get_user_tickets(user_id):
    """
    Lấy danh sách tất cả vé mà người dùng đã mua
    """
    tickets = db.session.query(
        Bill_Detail.id.label('bill_detail_id'),
        Bill_Detail.bought_quantity,
        Bill_Detail.code,
        Bill_Detail.used,
        Bill.id.label('bill_id'),
        Bill.status_ticket,
        Bill.created_date,
        Bill.total_price,
        Ticket.type.label('ticket_type'),
        Ticket.price.label('ticket_price'),
        Event.name.label('event_name'),
        Event.date.label('event_date'),
        Event.time.label('event_time'),
        Event.address.label('event_address'),
        Event.image.label('event_image')
    ).join(Bill, Bill_Detail.bill_id == Bill.id)\
     .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
     .join(Event, Ticket.event_id == Event.id)\
     .filter(Bill.user_id == user_id)\
     .order_by(desc(Bill.created_date))\
     .all()

    return tickets

def get_user_tickets_with_pagination(user_id, page=1, per_page=10):
    """
    Lấy danh sách vé của người dùng với phân trang
    """
    pagination = db.session.query(
        Bill_Detail.id.label('bill_detail_id'),
        Bill_Detail.bought_quantity,
        Bill_Detail.code,
        Bill_Detail.used,
        Bill.id.label('bill_id'),
        Bill.status_ticket,
        Bill.created_date,
        Bill.total_price,
        Ticket.type.label('ticket_type'),
        Ticket.price.label('ticket_price'),
        Event.name.label('event_name'),
        Event.date.label('event_date'),
        Event.time.label('event_time'),
        Event.address.label('event_address'),
        Event.image.label('event_image')
    ).join(Bill, Bill_Detail.bill_id == Bill.id)\
     .join(Ticket, Bill_Detail.ticket_id == Ticket.id)\
     .join(Event, Ticket.event_id == Event.id)\
     .filter(Bill.user_id == user_id)\
     .order_by(desc(Bill.created_date))\
     .paginate(page=page, per_page=per_page, error_out=False)

    return pagination
