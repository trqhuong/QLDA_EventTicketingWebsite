function update_cart_ui(cartInfo,id,type) {
    // Cập nhật tổng tiền
    const totalPriceElement = document.getElementById('total-price');
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
            if(parseInt(totalTicketsElementInput.value) > 0){

                let removeBtn = document.getElementById('removeBtn');
                if(removeBtn.disabled == true){
                    removeBtn.disabled = false
                }

            }

        }
    } else if(type == "REMOVE"){
        const totalTicketsElementInput = document.getElementById(`quantity-${id}`);
        if (totalTicketsElementInput) {
            let currentQuantity = parseInt(totalTicketsElementInput.value);
            totalTicketsElementInput.value = currentQuantity - 1;
            if(parseInt(totalTicketsElementInput.value) === 0){
                console.log("value = 0");
                let removeBtn = document.getElementById('removeBtn');
                if(removeBtn){
                   console.log("has btn");
                }
                removeBtn.disabled = true
            }
        }
    }

    document.getElementById('total_ticket').innerText = "Tổng số vé: " + cartInfo.total_ticket;
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
    .then(res => {
        if(!res.ok){
            throw new Error("Network response was not ok");
        }
        return res.json();
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
        // Bắt các lỗi xảy ra trong quá trình fetch hoặc khi xử lý response
        console.error("Lỗi khi gửi yêu cầu:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại sau.");
    });
}