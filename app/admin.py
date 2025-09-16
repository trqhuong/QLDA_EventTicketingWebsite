from flask import redirect, flash, request, url_for
from flask_admin import Admin,expose,  AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from app import db,app
from app.models import User,Role, ReviewStatus,TicketStatus, TypeTicket,  MyTicket_Status,EventType,Organizer,Event,Artist,Bill_Detail,Bill,Ticket
from flask_login import current_user, logout_user
from app.dao import bill_dao, bill_detail_dao

admin=Admin(app=app, name='Quản Trị Hệ Thống Bán Vé', template_mode='bootstrap4')

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')

    def is_accessible(self):
        return current_user.is_authenticated

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class AuthenticatedView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated or current_user.role != Role.ADMIN:
            logout_user()
            return False
        return True

class MyUserView(ModelView):
    column_list = ['id','role', 'username', 'email', 'phone']
    column_searchable_list = ['username']
    column_filters = ['role']
    # column_editable_list = ['phone']


# class AuthenticatedBaseView(BaseView):
#     def is_accessible(self):
#         return current_user.is_authenticated


# class LogoutView(AuthenticatedBaseView):
#     @expose("/")
#     def index(self):
#         logout_user()
#         return redirect('/admin')


class StatsView(BaseView):
    @expose("/")
    def index(self):
        # Lấy tham số lọc từ URL
        selected_year = request.args.get('year', type=int)
        selected_month = request.args.get('month', type=int)
        selected_quarter = request.args.get('quarter', type=int)

        # Lấy danh sách các năm có sự kiện (toàn hệ thống)
        years = bill_dao.get_admin_available_years()

        # Lấy dữ liệu thống kê tổng quan (toàn hệ thống)
        report_data = bill_dao.get_admin_report_data(selected_year, selected_month, selected_quarter)

        # Lấy dữ liệu cho biểu đồ - truyền cả tham số quarter (toàn hệ thống)
        monthly_events = bill_dao.get_admin_monthly_events_data(selected_year, selected_month, selected_quarter)
        monthly_revenue = bill_dao.get_admin_monthly_revenue_data(selected_year, selected_month, selected_quarter)

        # Lấy thống kê chi tiết sự kiện (toàn hệ thống)
        event_statistics = bill_dao.get_admin_event_statistics(selected_year, selected_month, selected_quarter)

        return self.render('admin/report_stats.html',
                               years=years,
                               selected_year=selected_year,
                               selected_month=selected_month,
                               selected_quarter=selected_quarter,
                               total_events=report_data['total_events'],
                               total_revenue=report_data['total_revenue'],
                               monthly_events=monthly_events,
                               monthly_revenue=monthly_revenue,
                               event_statistics=event_statistics)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.name == 'ADMIN'

class Check_Ticket_View(BaseView):
    @expose("/", methods=['GET', 'POST'])
    def index(self):
        ticket_info = None

        if request.method == 'POST':
            ticket_code = request.form.get('ticket_code', '').strip()

            if not ticket_code:
                flash('Vui lòng nhập mã vé!', 'error')
                return self.render('admin/Check_ticket.html')

            # Tìm kiếm vé theo mã code
            bill_detail = bill_detail_dao.get_ticket_by_code(ticket_code)

            if bill_detail:
                # Lấy thông tin chi tiết vé
                ticket_info = {
                    'code': bill_detail.code,
                    'used': bill_detail.used,
                    'quantity': bill_detail.bought_quantity,
                    'event_name': bill_detail.ticket.event.name,
                    'ticket_type': bill_detail.ticket.type.value,
                    'price': bill_detail.ticket.price,
                    'buyer_name': bill_detail.bill.user.username,
                    'buyer_email': bill_detail.bill.user.email,
                    'purchase_date': bill_detail.bill.created_date
                }

                if bill_detail.used:
                    flash('Vé này đã được sử dụng trước đó!', 'warning')
                else:
                    flash('Tìm thấy vé hợp lệ!', 'success')
            else:
                flash('Không tìm thấy vé với mã này!', 'error')

        return self.render('admin/Check_ticket.html', ticket_info=ticket_info)

    @expose("/scan", methods=['POST'])
    def scan_ticket(self):
        ticket_code = request.form.get('ticket_code', '').strip()

        if not ticket_code:
            flash('Vui lòng nhập mã vé!', 'error')
            return redirect(url_for('check_ticket_view.index'))

        # Tìm kiếm vé theo mã code
        bill_detail = bill_detail_dao.get_ticket_by_code(ticket_code)

        if bill_detail:
            # Lấy thông tin chi tiết vé
            ticket_info = {
                'code': bill_detail.code,
                'used': bill_detail.used,
                'quantity': bill_detail.bought_quantity,
                'event_name': bill_detail.ticket.event.name,
                'ticket_type': bill_detail.ticket.type.value,
                'price': bill_detail.ticket.price,
                'buyer_name': bill_detail.bill.user.username,
                'buyer_email': bill_detail.bill.user.email,
                'purchase_date': bill_detail.bill.created_date
            }

            return self.render('admin/Check_ticket.html', ticket_info=ticket_info)
        else:
            flash('Không tìm thấy vé với mã này!', 'error')
            return redirect(url_for('check_ticket_view.index'))

    @expose("/use", methods=['POST'])
    def use_ticket(self):
        ticket_code = request.form.get('ticket_code', '').strip()

        if not ticket_code:
            return redirect(url_for('check_ticket_view.index'))

        bill_detail_dao.mark_ticket_as_used(ticket_code)

        return redirect(url_for('check_ticket_view.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.name == 'ADMIN'

admin.add_view(MyUserView(User,db.session,name="Người dùng"))
admin.add_view(ModelView(Organizer,db.session, name="Nhà tổ chức"))
admin.add_view(StatsView(name='Thống kê doanh thu'))
admin.add_view(Check_Ticket_View(name='Quét vé'))
admin.add_view(LogoutView(name='Đăng xuất'))
