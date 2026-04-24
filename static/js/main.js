document.addEventListener("DOMContentLoaded", function() {

    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        setTimeout(function() {

            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";

            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });

    const checkoutBtn = document.querySelector('#checkout-btn');

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function(event) {

            alert("Processing your order... Thank you for choosing us!");
        });
    }
});