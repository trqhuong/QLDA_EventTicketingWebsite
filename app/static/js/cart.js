function update_cart_ui(cartInfo,id,type) {
    // Cập nhật tổng tiền

    const totalPriceElement = document.getElementById('total-price');
    const continueBtn = document.getElementById('continueBtn');
//    if(continueBtn) {
//        console.log("has btn continue");
//    }
    if (totalPriceElement) {
        totalPriceElement.innerText = "Tạm tính: " + cartInfo.total;
    }
    // Cập nhật tổng số vé cho input
    if(type == "ADD"){
        const totalTicketsElementInput = document.getElementById(`quantity-${id}`);
        if (totalTicketsElementInput) {
            let currentQuantity = parseInt(totalTicketsElementInput.value);
            if(isNaN(currentQuantity)){
                currentQuantity = 0;
            }
            totalTicketsElementInput.value = currentQuantity + 1;

        }
    } else if(type == "REMOVE"){
        const totalTicketsElementInput = document.getElementById(`quantity-${id}`);
        if (totalTicketsElementInput) {
            let currentQuantity = parseInt(totalTicketsElementInput.value);
            totalTicketsElementInput.value = currentQuantity - 1;
        }
    }
    document.getElementById('total_ticket').innerText = "Tổng số vé: " + cartInfo.total_ticket;
    if(parseInt(cartInfo.total_ticket) === 0){
        continueBtn.disabled = true;
    } else {
        continueBtn.disabled = false;
    }
}

function add_to_cart(id, event_name, type, price) {
    // axios fetch
    fetch('/api/cart',{
        method : 'post',
        body: JSON.stringify({
            "ticket_id": id,
            "event_name" : event_name,
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
            update_cart_ui(data,id,'ADD');
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
            update_cart_ui(data,id,'REMOVE');
        }


    })
    .catch(error => {
        // Bắt lỗi được ném ra từ khối .then() ở trên
        // error.message chính là thông điệp lỗi từ server
        console.error("Lỗi khi gửi yêu cầu:", error.message);
        alert(error.message);
    });
}

function handleOnclick (cart) {
    window.location.href = `http://127.0.0.1:5000/book_ticket`;
}