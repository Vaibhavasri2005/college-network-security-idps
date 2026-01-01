// Login Form Handler

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const loginButton = document.getElementById('login-button');
    const buttonText = loginButton.querySelector('.button-text');
    const spinner = loginButton.querySelector('.spinner');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Hide messages
        hideMessage(errorMessage);
        hideMessage(successMessage);

        // Show loading state
        setLoading(true);

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show success message
                showMessage(successMessage, '✓ Login successful! Redirecting...');
                
                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                // Show error message
                const errorMsg = data.message || 'Invalid username or password';
                showMessage(errorMessage, '✕ ' + errorMsg);
                setLoading(false);
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage(errorMessage, '✕ Connection error. Please try again.');
            setLoading(false);
        }
    });

    function setLoading(loading) {
        loginButton.disabled = loading;
        if (loading) {
            buttonText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            buttonText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    function showMessage(element, message) {
        element.textContent = message;
        element.classList.remove('hidden');
    }

    function hideMessage(element) {
        element.classList.add('hidden');
    }

    // Auto-hide error messages after 5 seconds
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.target === errorMessage && !errorMessage.classList.contains('hidden')) {
                setTimeout(() => {
                    hideMessage(errorMessage);
                }, 5000);
            }
        });
    });

    observer.observe(errorMessage, { attributes: true, attributeFilter: ['class'] });
});
