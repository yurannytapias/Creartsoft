const OpenModal = document.getElementById('openModal');
const Modal = document.getElementById('modal')
const CloseModal = document.getElementById('close_modal');

OpenModal.addEventListener('click', () =>  {
    Modal.classList.add('active');
})

CloseModal.addEventListener('click', () => {
    Modal.classList.remove('active');
})

// Cerrar al hacer clic fuera del modal
modalOverlay.addEventListener('click', (e) => {
  if (e.target === modalOverlay) {
    modalOverlay.classList.remove('active');
  }
});