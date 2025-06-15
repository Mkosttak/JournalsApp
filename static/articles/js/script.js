// PDF File Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    const changePdfBtn = document.getElementById('change-pdf-btn');
    const pdfInput = document.getElementById('id_file');
    const currentPdfName = document.getElementById('current-pdf-name');
    const currentPdfLink = document.getElementById('current-pdf-link');
    const changePdfBtnText = document.getElementById('change-pdf-btn-text');

    if (changePdfBtn && pdfInput) {
        changePdfBtn.addEventListener('click', function() {
            pdfInput.click();
        });

        pdfInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                currentPdfName.textContent = fileName;
                currentPdfName.setAttribute('data-original-name', fileName);
                
                // Update button text
                if (changePdfBtnText) {
                    changePdfBtnText.textContent = 'PDF Güncelle';
                }

                // Remove the link if it exists
                if (currentPdfLink) {
                    const parent = currentPdfLink.parentNode;
                    parent.replaceChild(currentPdfName, currentPdfLink);
                }

                // Dosya seçildiğinde form otomatik olarak gönderilsin
                const form = pdfInput.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }
}); 