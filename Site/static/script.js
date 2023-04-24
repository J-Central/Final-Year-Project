function showModal(modalName) {
    const d = document.getElementById(modalName);
    d.showModal()
}

function selectAll(select_all) {
    var items = document.getElementsByName('select_item');
    for(var i=0, n=items.length; i<n; i++) {
        items[i].checked = select_all.checked;
    }
}

function deleteItem() {
    var check_list = Array.from(document.querySelectorAll("input.select_item:checked"));
    console.log(check_list)
    for(var i=0, n=check_list.length; i<n; i++) {
        check_list[i].closest('form').submit();
    }
}

async function refresh_item(e) {
    item_url = e.parentNode.querySelector("input").getAttribute("value")
    f = new FormData()
    f.append("select_item", item_url);
    await fetch("/refresh_item", {
        method: "POST",
        body: f
    });
    document.location = "/homepage";
}

async function purchased(current) {
    var value = current.getAttribute('data-value');
    var item = [value];

    try {
        await fetch("/purchased", {
            method: "POST",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(item) 
        });
        var source = current.getAttribute('src');
        if (source == "../static/assets/check.svg") {
            current.src = "../static/assets/cross.svg";      
        }
        else {
            current.src = "../static/assets/check.svg";  
        }
    } catch(error) {
        console.log(error, ':(')
    }
}

function doesUserWantToLogout() {
    if (confirm("Are you sure you want to logout?")) {
        window.location = "/logout"
    }
}