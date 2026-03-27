const OpenModalMio = document.getElementById('openModalMio');
const ModalMio = document.getElementById('modal_mio')
const CloseModalMio = document.getElementById('close_modalMio');

OpenModalMio.addEventListener('click', () =>  {
    ModalMio.classList.add('active');
})

CloseModalMio.addEventListener('click', () => {
    ModalMio.classList.remove('active');
})

// Cerrar al hacer clic fuera del modal
CloseModalMio.addEventListener('click', (e) => {
  if (e.target === CloseModalMio) {
    ModalMio.classList.remove('active');
  }
});