document.addEventListener('DOMContentLoaded', function() {
  MicroModal.init({
    disableScroll: true,
    awaitCloseAnimation: true
  });

  let deleteUrl = null;
  let postElement = null;

  function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return '';
  }

// Prepare delete action (called from HTML)
  window.prepareDelete = function(button) {
    deleteUrl = button.dataset.deleteUrl;
    postElement = button.closest('.post-card');
    MicroModal.show('deleteModal');
  };

  // Confirm delete
  const confirmDeleteButton = document.getElementById('confirmDelete');
  if (confirmDeleteButton) {
    confirmDeleteButton.addEventListener('click', function() {
      if (!deleteUrl || !postElement) return;

      fetch(deleteUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json'
        },
      })
      .then(response => {
        if (response.ok) {
          // Remove the post card
          const dateSection = postElement.closest('.date-section');
          const accordion = postElement.closest('.posts-accordion');
          
          postElement.remove();
          
          // Check if this was the last post in the date section
          const remainingPosts = accordion.querySelectorAll('.post-card');
          if (remainingPosts.length === 0) {
            // Remove the entire date section
            dateSection.remove();
            
            // Check if there are any date sections left
            const remainingSections = document.querySelectorAll('.date-section');
            if (remainingSections.length === 0) {
              // Show "no posts" message
              const container = document.querySelector('.dashboard-container');
              const actionBar = container.querySelector('.action-bar');
              
              const noPostsHTML = `
                <div class="no-posts">
                  <div class="no-posts-icon">📝</div>
                  <div class="no-posts-text">No journal entries yet</div>
                  <a href="/posts/create/" class="btn-new-entry">
                    <i class="fas fa-plus-circle"></i>
                    Start Your First Entry
                  </a>
                </div>
              `;
              
              actionBar.insertAdjacentHTML('afterend', noPostsHTML);
            }
          } else {
            // Update entry count in date header
            const dateHeader = dateSection.querySelector('.date-header');
            const entryCount = dateHeader.querySelector('.entry-count');
            const count = remainingPosts.length;
            entryCount.textContent = `${count} ${count === 1 ? 'entry' : 'entries'}`;
          }
          
          MicroModal.close('deleteModal');
          
          // Reset variables
          deleteUrl = null;
          postElement = null;
        } else {
          console.error("Failed to delete post");
          alert("Failed to delete post. Please try again.");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
    });
  }

  // Calendar toggle (placeholder for future feature)
  const calendarToggle = document.getElementById('calendarToggle');
  if (calendarToggle) {
    calendarToggle.addEventListener('click', function() {
      alert('Calendar view coming soon! 📅');
      // TODO: Implement calendar view
    });
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Escape key closes expanded posts
    if (e.key === 'Escape') {
      document.querySelectorAll('.post-card.expanded').forEach(card => {
        card.classList.remove('expanded');
        const button = card.querySelector('.btn-expand');
        if (button) {
          button.querySelector('.expand-text').textContent = 'Read Full';
          button.querySelector('i').className = 'fas fa-expand-alt';
        }
      });
    }
    
    // Ctrl/Cmd + N for new entry
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      window.location.href = '/posts/create/';
    }
  });

  // Add smooth scroll to date sections
  const urlParams = new URLSearchParams(window.location.search);
  const scrollToDate = urlParams.get('date');
  
  if (scrollToDate) {
    const dateSection = document.querySelector(`[data-date="${scrollToDate}"]`);
    if (dateSection) {
      dateSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const header = dateSection.querySelector('.date-header');
      if (header && !header.classList.contains('active')) {
        toggleDateSection(header);
      }
    }
  }
});