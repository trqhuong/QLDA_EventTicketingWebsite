from unittest.mock import patch
from app.index import pay,vnpay_return
from app import app


@patch("app.index.vnpay_dao.vnpay")
@patch("app.index.redirect")
def test_pay_builds_vnpay_url(mock_redirect, mock_vnpay):
    mock_vnpay_instance = mock_vnpay.return_value
    mock_vnpay_instance.get_payment_url.return_value = "https://fake-vnpay-url"

    with app.test_request_context(
        path="/pay_via_VNPAY",
        method="POST",
        data={"eventId": "123", "amount": "100000"}
    ):
        result = pay()

    mock_redirect.assert_called_once_with("https://fake-vnpay-url")
    assert result == mock_redirect.return_value


    # assert
    mock_redirect.assert_called_once_with("https://fake-vnpay-url")
    assert result == mock_redirect.return_value


# -----------------------------
# Case 1: Thanh toán thành công
# -----------------------------
@patch("app.index.vnpay_dao.verify_return", return_value=True)
@patch("app.index.bill_dao.create_bill_bill_detail", return_value={"id": 1})
@patch("app.index.utils.send_invoice")
@patch("app.index.flash")
@patch("app.index.redirect")
@patch("app.index.current_user")
def test_vnpay_return_success(mock_user, mock_redirect, mock_flash,
                              mock_send_invoice, mock_create_bill, mock_verify):

    mock_user.email = "test@example.com"
    mock_redirect.return_value = "redirected"

    # Giả lập request args
    with app.test_request_context(
        "/vnpay_return?vnp_ResponseCode=00&vnp_TransactionStatus=00"
    ):
        result = vnpay_return()

    # Assertions
    mock_verify.assert_called_once()
    mock_create_bill.assert_called_once()
    mock_send_invoice.assert_called_once()
    mock_flash.assert_called_once_with("Thanh toán thành công!", "success")
    assert result == "redirected"


# -----------------------------
# Case 2: Sai chữ ký
# -----------------------------
@patch("app.index.vnpay_dao.verify_return", return_value=False)
def test_vnpay_return_invalid_signature(mock_verify):
    with app.test_request_context(
        "/vnpay_return?vnp_ResponseCode=00&vnp_TransactionStatus=00"
    ):
        result = vnpay_return()

    assert isinstance(result, tuple)
    assert result[1] == 400
    assert "Sai chữ ký" in result[0]



# -----------------------------
# Case 3: Giao dịch thất bại
# -----------------------------
@patch("app.index.vnpay_dao.verify_return", return_value=True)
def test_vnpay_return_fail(mock_verify):
    with app.test_request_context(
        "/vnpay_return?vnp_ResponseCode=99&vnp_TransactionStatus=01"
    ):
        result = vnpay_return()

    assert "Giao dịch thất bại" in result