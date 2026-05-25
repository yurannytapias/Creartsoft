from django.test import TestCase

# Create your tests here.

from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages

from creart.models import Usuarios, Roles

class TestAutenticacion(TestCase):

    def setUp(self):
        self.client = Client()

        self.rol_cliente = Roles.objects.create(
            nombre="cliente"
        )

        self.usuario_test = Usuarios.objects.create(
            nombre="Juan",
            apellido="Pérez",
            correo="juan@test.com",
            numero="3001234567",
            contrasena=make_password("Test@1234"),
            rol=self.rol_cliente
        )

    def test_tc001_login_credenciales_validas(self):

        response = self.client.post('/login/', {
            'correo': 'juan@test.com',
            'contrasena': 'Test@1234'
        })

        self.assertEqual(response.status_code, 302)
    # TC-002
    def test_tc002_login_correo_inexistente(self):

        response = self.client.post('/login/', {
            'correo': 'noexiste@test.com',
            'contrasena': 'Test@1234'
        })

        # Verifica redirección
        self.assertEqual(response.status_code, 302)

        # Obtener mensajes
        messages = list(get_messages(response.wsgi_request))

        # Verificar mensaje
        self.assertEqual(
            str(messages[0]),
            "No existe una cuenta con ese correo electrónico."
        )

        # Verificar que NO inició sesión
        self.assertNotIn('usuario_id', self.client.session)



# TC-003
    def test_tc003_login_contrasena_incorrecta(self):

        response = self.client.post('/login/', {
            'correo': 'juan@test.com',
            'contrasena': 'ContraseñaIncorrecta'
        })

        # Verifica redirección
        self.assertEqual(response.status_code, 302)

        # Obtener mensajes
        messages = list(get_messages(response.wsgi_request))

        # Verificar mensaje
        self.assertEqual(
            str(messages[0]),
            "La contraseña es incorrecta. Por favor, inténtalo de nuevo."
        )

        # Verificar que NO inició sesión
        self.assertNotIn('usuario_id', self.client.session)
# TC-004
    def test_tc004_login_campo_vacio(self):

        response = self.client.post('/login/', {
            'correo': '',
            'contrasena': 'Test@1234'
        })

        # Verifica redirección
        self.assertEqual(response.status_code, 302)

        # Obtener mensajes
        messages = list(get_messages(response.wsgi_request))

        # Verificar mensaje
        self.assertEqual(
            str(messages[0]),
            "Por favor, completa todos los campos obligatorios."
        )

        # Verificar que NO inició sesión
        self.assertNotIn('usuario_id', self.client.session)
        