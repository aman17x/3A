document.addEventListener('DOMContentLoaded', () => {
    console.log("main.js loaded ✅");

    // ====================
    // DELETE POST LOGIC
    // ====================
    const deleteButtons = document.querySelectorAll('.delete-btn');
    console.log(`Found ${deleteButtons.length} delete buttons`);

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', async() => {
            const postId = btn.getAttribute('data-post-id');
            if (!confirm('Delete this artwork?')) return;

            try {
                const resp = await fetch(`/api/posts/${postId}/delete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const result = await resp.json();
                if (result.success) {
                    // Smooth fade-out before removing
                    const card = btn.closest('.art-card');
                    card.style.transition = 'opacity 0.3s ease';
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                } else {
                    alert('Error: ' + (result.error || 'Could not delete'));
                }
            } catch (err) {
                console.error('❌ Delete request failed:', err);
                alert('Network error — please try again');
            }
        });
    });

    // ====================
    // CHAT SEND LOGIC
    // ====================
    const chatForm = document.getElementById('chatForm');
    const msgInput = document.getElementById('msgInput');
    const messagesDiv = document.getElementById('messages');

    if (chatForm) {
        chatForm.addEventListener('submit', async e => {
            e.preventDefault();
            const text = msgInput.value.trim();
            if (!text) return;

            try {
                const resp = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const result = await resp.json();
                if (result.success) {
                    // Create and prepend new message
                    const p = document.createElement('p');
                    p.innerHTML = `<strong>You:</strong> ${text}`;
                    messagesDiv.prepend(p);

                    // Clear input
                    msgInput.value = '';
                } else {
                    alert('Error sending message: ' + (result.error || 'Unknown error'));
                }
            } catch (err) {
                console.error('❌ Chat send failed:', err);
                alert('Network error — please try again');
            }
        });
    }

    // ====================
    // OPTIONAL: Auto-scroll chat to newest message
    // ====================
    if (messagesDiv) {
        messagesDiv.scrollTop = 0; // top if newest first
        // or messagesDiv.scrollTop = messagesDiv.scrollHeight; // bottom if oldest first
    }
});
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('theme-toggle');
  if (!toggleBtn) return;

  // Load saved theme from localStorage
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark');
    toggleBtn.textContent = '☀️'; // sun icon for light mode
  }

  toggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
      toggleBtn.textContent = '☀️';
      localStorage.setItem('theme', 'dark');
    } else {
      toggleBtn.textContent = '🌙';
      localStorage.setItem('theme', 'light');
    }
  });
});
document.addEventListener('click', async function(e) {
    if (e.target.classList.contains('like-btn')) {
        const section = e.target.closest('.like-section');
        const postId = section.getAttribute('data-post-id');
        const res = await fetch(`/like/${postId}`, { method: 'POST' });
        const data = await res.json();
        section.querySelector('.like-count').textContent = data.likes;
        if (data.status === 'liked') {
            e.target.classList.add('liked');
        } else {
            e.target.classList.remove('liked');
        }
    }
});
