// Authentication state management
const checkAuth = () => {
    const token = localStorage.getItem('token');
    const authButtons = document.getElementById('auth-buttons');
    
    if (token) {
        authButtons.innerHTML = `
            <button onclick="logout()" class="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">Logout</button>
            <a href="/dashboard" class="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700">Dashboard</a>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="/login" class="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium">Login</a>
            <a href="/register" class="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700">Register</a>
        `;
    }
};

// Logout function
const logout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
};

// Copy to clipboard function
const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
};

// Toast notification
const showToast = (message, type = 'success') => {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded-md text-white ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } transition-opacity duration-300`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
};

// Loading spinner
const showLoading = (element) => {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
    return spinner;
};

const hideLoading = (spinner) => {
    if (spinner && spinner.parentElement) {
        spinner.parentElement.removeChild(spinner);
    }
};

// Form validation
const validateForm = (formElement) => {
    const inputs = formElement.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
            
            const errorMessage = document.createElement('p');
            errorMessage.className = 'text-red-500 text-xs mt-1';
            errorMessage.textContent = 'This field is required';
            
            const existingError = input.parentElement.querySelector('.text-red-500');
            if (!existingError) {
                input.parentElement.appendChild(errorMessage);
            }
        } else {
            input.classList.remove('border-red-500');
            const existingError = input.parentElement.querySelector('.text-red-500');
            if (existingError) {
                existingError.remove();
            }
        }
    });
    
    return isValid;
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Setup form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}); 