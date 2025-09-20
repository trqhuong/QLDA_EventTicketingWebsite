from app import db
from app.models import Bill_Detail, Bill, Ticket, Event, User
from sqlalchemy.orm import joinedload

def get_ticket_by_code(ticket_code):
    """
    Tìm kiếm thông tin vé theo mã code
    """
    if not ticket_code:
        return None
    try:
        bill_detail = db.session.query(Bill_Detail)\
            .join(Bill)\
            .join(Ticket)\
            .join(Event)\
            .join(User)\
            .filter(Bill_Detail.code == ticket_code)\
            .first()

        return bill_detail
    except Exception as e:
        print(f"Error getting ticket by code: {e}")
        return None

def mark_ticket_as_used(ticket_code):
    """
    Đánh dấu vé đã sử dụng theo mã code
    """
    try:
        bill_detail = Bill_Detail.query.filter_by(code=ticket_code).first()

        if bill_detail:
            if bill_detail.used:
                return {
                    'success': False,
                    'message': 'Vé này đã được sử dụng trước đó!',
                    'type': 'warning'
                }
            else:
                bill_detail.used = True
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Đã đánh dấu vé sử dụng thành công!',
                    'type': 'success'
                }
        else:
            return {
                'success': False,
                'message': 'Không tìm thấy vé với mã này!',
                'type': 'error'
            }
    except Exception as e:
        db.session.rollback()
        print(f"Error marking ticket as used: {e}")
        return {
            'success': False,
            'message': 'Có lỗi xảy ra khi cập nhật vé!',
            'type': 'error'
        }
