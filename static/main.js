document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.querySelector('[data-menu-toggle]');

  if (sidebar && toggle) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    sidebar.querySelectorAll('.nav').forEach((link) => {
      link.addEventListener('click', () => sidebar.classList.remove('open'));
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') sidebar.classList.remove('open');
    });
  }
});
