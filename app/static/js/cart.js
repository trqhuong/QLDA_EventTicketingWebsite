function formatVND(amount) {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") + " ₫";
}
function update_cart_ui(cartInfo) {
    const totalPriceElement = document.getElementById('total-price');
    const continueBtn = document.getElementById('continueBtn');
    if (totalPriceElement) {
        totalPriceElement.innerText = "Tạm tính: " + formatVND(cartInfo.total);
    }
    document.getElementById('total_ticket').innerText = "Tổng số vé: " + cartInfo.total_ticket;
    continueBtn.replaceWith(continueBtn.cloneNode(true));
    const newBtn = document.getElementById('continueBtn');

    newBtn.addEventListener("click", () => {
        const eventId = newBtn.dataset.eventId;
        const totalTicket = cartInfo.total_ticket;
        handleContinuePayment(eventId, totalTicket);
    });
}
function handleContinuePayment (eventId, total_ticket) {

    if(total_ticket == 0){
        alert("Vui lòng chọn vé để tiếp tục");
        return;
    }

    window.location.href = `http://127.0.0.1:5000/book_ticket?event_id=${eventId}`;
}
function add_to_cart(id, type, price) {
    // axios fetch
    fetch('/api/cart',{
        method : 'post',
        body: JSON.stringify({
            "ticket_id": id,
            "type" : type,
            "price" : price
        }),
        headers : {
            "Content-Type" : "application/json"
        }
    })
    .then(res => {
        if(!res.ok){
            throw new Error("Network response was not ok");
        }
//        console.log("JSON return: ",res.json());
        return res.json();
    })
    .then(data => {
        if(data.error){
            console.log("Server error",data.error);
        } else {
            console.info("Add ticket successfull");
            update_cart_ui(data);
        }
    })
    .catch(error => {
        // Bắt các lỗi xảy ra trong quá trình fetch hoặc khi xử lý response
        console.error("Lỗi khi gửi yêu cầu:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại sau.");
    });
}

function remove_from_cart(id) {
    console.log("received :", id);
    // axios fetch
    fetch('/api/cart',{
        method : 'put',
        body: JSON.stringify({
            "ticket_id": id,
        }),
        headers : {
            "Content-Type" : "application/json"
        }
    })
    // Xử lí response trả về từ server
    .then(res => {
        // Nhận dữ liệu JSON từ server, parse thành Javacript để xử lí dữ liệu (Deserialize)
        return res.json().then(data => {
            if (!res.ok) {
                // Nếu response không thành công, ném lỗi với thông điệp từ server
                // data.error sẽ chứa "Cannot update ticket has quantity = 0"
                throw new Error(data.error);
            }
            // Nếu thành công, trả về dữ liệu bình thường
            return data;
        });
        // JSON -> Javascript
    })
    .then(data => {
        if(data.error){
            console.log("Server error",data.error);
        } else {
            console.info("Remove ticket successfull");
            update_cart_ui(data);
        }
    })
    .catch(error => {
        // Bắt lỗi được ném ra từ khối .then() ở trên
        // error.message chính là thông điệp lỗi từ server
        console.error("Lỗi khi gửi yêu cầu:", error.message);
        alert(error.message);
    });
}


function handleAdd(ticketId,quantity,type, price) {
    let inputElement = document.getElementById(`quantity-${ticketId}`);
    if(inputElement) {
        let currentQuantity = parseInt(inputElement.value);

        currentQuantity += 1;
        if(currentQuantity > parseInt(quantity)){
            alert("Vé đã hết hoặc đặt quá số lượng");
            return;
        }
        inputElement.value = currentQuantity;
        add_to_cart(ticketId, type, price);
        console.log("Current: ", currentQuantity);
    }

}

function handleRemove(ticketId, quantity) {
    let inputElement = document.getElementById(`quantity-${ticketId}`);
    if(inputElement) {
        let currentQuantity = parseInt(inputElement.value);
        currentQuantity -= 1;
        if(currentQuantity < 0){
            alert("Bạn không thể giảm thêm được nữa!!");
            return;
        }
        inputElement.value = currentQuantity;
        remove_from_cart(ticketId)
    }

}