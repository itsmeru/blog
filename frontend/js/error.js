class ErrorHandler {
    static showError(message) {
        // 創建錯誤訊息元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error';
        errorDiv.textContent = message;
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '100px';
        errorDiv.style.left = '50%';
        errorDiv.style.transform = 'translateX(-50%)';
        errorDiv.style.zIndex = '9999';
        errorDiv.style.minWidth = '300px';
        errorDiv.style.textAlign = 'center';
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 2000);
    }

    static showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'message success';
        successDiv.textContent = message;
        successDiv.style.position = 'fixed';
        successDiv.style.top = '100px';
        successDiv.style.left = '50%';
        successDiv.style.transform = 'translateX(-50%)';
        successDiv.style.zIndex = '9999';
        successDiv.style.minWidth = '300px';
        successDiv.style.textAlign = 'center';
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.remove();
        }, 2000);
    }
}