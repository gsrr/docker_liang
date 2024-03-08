//此檔案為暫時放置比對用, 之後會刪除
function sendScannedData(scannedData) {
    const csrfToken = getCookie('csrftoken');
    fetch('/handle_scanned_data/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({'scanned_data': scannedData})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('后端验证成功:', data.message);
            document.getElementById('scanned-result').value = data.barcode; // 更新输入框内容
        } else {
            console.error('后端验证失败:', data.message);
            // 可以选择在此显示错误信息
        }
    })
    .catch(error => console.error('发送数据错误:', error));
}


function sendScannedData(scannedData) {
    const csrfToken = getCookie('csrftoken'); // 获取CSRF令牌
    fetch('/handle_scanned_data/', { // 更新为新的URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({'scanned_data': scannedData})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('网络响应错误，状态码：' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log('后端验证成功:', data.message);
            var textarea = document.getElementById('scanned-results');
            textarea.value += data.barcode + "\n"; // 追加新数据并换行
        } else {
            console.error('后端验证失败:', data.message);
            alert("无法匹配京都瑞龙货号，请切换为英数输入法或确认QR Code是否属于京都瑞龙");
            // 可以选择在此显示错误信息
        }
    })
    .catch(error => console.error('发送数据错误:', error));
}