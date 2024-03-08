let isScanning = false;
let scanBuffer = '';
let scanTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('start-scan').addEventListener('click', function() {
        isScanning = true;
        console.log('开始扫描');

        // 创建一个隐藏的输入框用于接收扫描数据
        const input = document.createElement('input');
        input.type = 'text';
        input.style.position = 'absolute';
        input.style.opacity = 0;
        input.id = 'hidden-input';
        document.body.appendChild(input);
        input.focus();

        // 输入事件监听器
        input.addEventListener('input', function(event) {
            clearTimeout(scanTimer); // 清除已存在的计时器
            scanBuffer += event.target.value; // 累加输入内容到缓冲区
            event.target.value = ''; // 清空输入框

            // 设置计时器，延迟处理输入
            scanTimer = setTimeout(function() {
                if (isScanning && scanBuffer.trim()) {
                    const scannedContent = scanBuffer.trim();
                    console.log('扫描到的内容:', scannedContent);
                    handleScannedData(scannedContent); // 發送給另外一個js函數處理,非關鍵數據不要發送給後端
                    scanBuffer = ''; // 清空缓冲区
                }
            }, 50); // 50毫秒延迟，根据需要调整
        });
    });

    document.getElementById('stop-scan').addEventListener('click', function() {
    var scannedBarcodes = document.getElementById('scanned-results').value.trim();
    if (scannedBarcodes) {
        updateItemNotes(scannedBarcodes);
    }
    });

    function updateItemNotes(scannedBarcodes) {
    fetch('/update_item_notes/', { // 根据需要调整URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'unit_id': unitId, // 确保unitId变量在作用域中可用
            'scanned_barcodes': scannedBarcodes
        })
    })
    .then(response => response.json())
    .then(data => {
    if (data.status === 'success') {
        console.log('Item notes updated:', data.message);
        // 重定向到新的URL
        window.location.href = '/manage-rentalspace/' + data.space_id + '/';
    } else {
        alert(data.message); // 使用alert显示错误信息
    }
})
.catch(error => {
    console.error('请求处理错误:', error);
    alert('请求处理错误: ' + error.message); // 显示请求错误
});


}






});

function handleScannedData(scannedData) {
    const pattern = /(\d{4})\/([a-zA-Z]{1,3}\d{6})$/;
    const match = pattern.exec(scannedData);
    if (match) {
        const year = match[1].substr(-2);  // 获取年份的最后两位
        const itemNumber = match[2];       // 获取货号
        const formattedBarcode = `${itemNumber}-${year}`; // 格式化输出
        // 更新输入框或其他元素以显示结果
        document.getElementById('scanned-results').value += formattedBarcode + "\n";
    } else {
        // 处理不匹配的情况
        console.error('无效的货号格式');
    }
}


// 用于获取CSRF令牌的辅助函数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
