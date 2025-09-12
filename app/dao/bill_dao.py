
from app.models import Bill, Bill_Detail, db, MyTicket_Status
from app.dao import user_dao,ticket_dao
from datetime import datetime
from app import utils



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
         bill_detail = Bill_Detail(
             bill_id = bill.id,
             ticket_id = int(item['ticket_id']),
             bought_quantity = int(item['quantity']),
         )
         db.session.add(bill_detail)
     db.session.commit()
     return bill