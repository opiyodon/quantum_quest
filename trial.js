document.addEventListener('DOMContentLoaded', function () {
    const profileImg = document.getElementById('profile-img');
    const profileBtn = document.getElementById('profile-btn');
    const profileModal = document.getElementById('profile-modal');
    const closeModal = document.getElementsByClassName('close')[0];
    const profileForm = document.getElementById('profile-form');
    const deleteAccountBtn = document.getElementById('delete-account');

    profileImg.onclick = function(event) {
        event.stopPropagation();
        const dropdownContent = document.querySelector('.dropdown-content');
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    }

    profileBtn.onclick = function() {
        profileModal.style.display = "block";
    }

    closeModal.onclick = function() {
        profileModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == profileModal) {
            profileModal.style.display = "none";
        }
        if (!event.target.matches('#profile-img')) {
            const dropdowns = document.getElementsByClassName("dropdown-content");
            for (let i = 0; i < dropdowns.length; i++) {
                let openDropdown = dropdowns[i];
                if (openDropdown.style.display === 'block') {
                    openDropdown.style.display = 'none';
                }
            }
        }
    }

    // Rest of your existing JavaScript code...
});