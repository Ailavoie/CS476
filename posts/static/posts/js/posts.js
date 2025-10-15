document.addEventListener('DOMContentLoaded', function() {
  MicroModal.init();

  let deleteUrl = null;
  let postElement = null;

  document.querySelectorAll('[data-micromodal-trigger="deleteModal"]').forEach(button => {
    button.addEventListener('click', function() {
      deleteUrl = this.dataset.deleteUrl;
      postElement = this.closest('.post-item');
    });
  });

  const confirmDeleteButton = document.getElementById('confirmDelete');
  confirmDeleteButton.addEventListener('click', function() {
    if (!deleteUrl) return;

    fetch(deleteUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
    })
    .then(response => {
      if (response.ok) {
        postElement.remove();
        MicroModal.close('deleteModal');

        if (document.querySelectorAll('.post-item').length === 0) {
          const postsList = document.querySelector('.posts-list');
          if (postsList) postsList.remove();

          const container = document.querySelector('.posts-container');
          const noPostsMessage = document.createElement('p');
          noPostsMessage.classList.add('no-posts');
          noPostsMessage.textContent = 'No posts yet.';
          container.appendChild(noPostsMessage);
        }
      } else {
        console.error("Failed to delete post");
      }
    })
    .catch(error => console.error("Error:", error));
  });

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
});
