/**
 * ArticlesApp - Modern Tasarım JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animasyonlu giriş efektleri
    const animateElements = document.querySelectorAll('.slide-up, .fade-in');
    
    if (animateElements.length > 0) {
        animateElements.forEach(element => {
            // Elementlerin görünür olduğundan emin olalım
            element.style.opacity = '1';
        });
    }
    
    // Profil resmi yükleme işlevi
    const imageUploadOverlay = document.querySelector('.image-upload-overlay');
    const profileImageInput = document.querySelector('input[type="file"][name="profile_image"]');
    
    if (imageUploadOverlay && profileImageInput) {
        imageUploadOverlay.addEventListener('click', function() {
            profileImageInput.click();
        });
        
        // Resim seçildiğinde önizleme göster
        profileImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                const profileImage = document.querySelector('.profile-image, .profile-image-placeholder');
                
                reader.onload = function(e) {
                    // Eğer img elementi varsa src'yi güncelle, yoksa yeni bir img elementi oluştur
                    if (profileImage.tagName === 'IMG') {
                        profileImage.src = e.target.result;
                    } else {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.classList.add('profile-image');
                        img.alt = 'Profil Fotoğrafı';
                        
                        // Eski placeholder'ı kaldır ve yeni img elementini ekle
                        profileImage.parentNode.replaceChild(img, profileImage);
                    }
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Form doğrulama geliştirmeleri
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const requiredInputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        requiredInputs.forEach(input => {
            // Giriş alanlarına focus sınıfı ekle/kaldır
            input.addEventListener('focus', function() {
                this.closest('.form-group').classList.add('is-focused');
            });
            
            input.addEventListener('blur', function() {
                this.closest('.form-group').classList.remove('is-focused');
                
                // Boş alan kontrolü
                if (this.value.trim() === '') {
                    this.closest('.form-group').classList.add('is-invalid');
                } else {
                    this.closest('.form-group').classList.remove('is-invalid');
                }
            });
        });
    });
    
    // Uyarı mesajları için otomatik kapanma
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5 saniye sonra kapat
    });
});