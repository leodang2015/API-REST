<script setup>
import { onMounted, ref } from 'vue'
import AdminDashboard from './AdminDashboard.vue'

const API_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
const accessToken = ref(sessionStorage.getItem('access_token') || '')
const refreshToken = ref(sessionStorage.getItem('refresh_token') || '')
const user = ref(null)
const demoMode = ref(false)
const authMode = ref('login')
const name = ref('')
const email = ref('')
const password = ref('')
const passwordConfirmation = ref('')
const busy = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const checkingSession = ref(Boolean(accessToken.value))

const demoAuthor = { id: 1, nombre: 'Gabriel García Márquez', nacionalidad: 'Colombiana', anio_nacimiento: 1927 }
const demoCategory = { id: 1, nombre: 'Novela', descripcion: 'Narrativa de ficción' }
const demoMember = { id: 2, nombre: 'Usuario de demostración', email: 'usuario@demo.local', telefono: '555-0100', activo: true }
const demoBook = {
  id: 1,
  titulo: 'Cien años de soledad',
  isbn: '9780307474728',
  descripcion: 'Una novela de ejemplo para recorrer el catálogo.',
  anio_publicacion: 1967,
  ejemplares: 4,
  disponible: 2,
  creado_en: '2026-01-15T12:00:00Z',
  portada_url: null,
  autor: { id: demoAuthor.id, nombre: demoAuthor.nombre },
  categorias: [{ id: demoCategory.id, nombre: demoCategory.nombre }],
}
const demoLoan = {
  id: 1,
  socio_id: demoMember.id,
  libro_id: demoBook.id,
  fecha_prestamo: '2026-11-20T12:00:00Z',
  fecha_limite: '2026-11-30T12:00:00Z',
  fecha_devolucion: null,
  multa: 0,
  devuelto: false,
  socio: demoMember,
  libro: demoBook,
}
const demoRequest = {
  id: 1,
  socio_id: demoMember.id,
  libro_id: demoBook.id,
  fecha_solicitud: '2026-11-22T12:00:00Z',
  estado: 'pendiente',
  fecha_entrega_estimada: null,
  socio: demoMember,
  libro: demoBook,
}
const demoProduct = {
  id: 1,
  nombre: 'Separador de libros',
  descripcion: 'Producto de ejemplo',
  precio: 2.5,
  stock: 12,
  activo: true,
  creado_en: '2026-01-15T12:00:00Z',
  categoria: { id: demoCategory.id, nombre: demoCategory.nombre },
}
const demoUsers = [
  { id: 1, nombre: 'Bibliotecario de demostración', email: 'bibliotecario@demo.local', role: 'bibliotecario', is_active: true, created_at: '2026-01-15T12:00:00Z' },
  { id: demoMember.id, nombre: demoMember.nombre, email: demoMember.email, role: 'cliente', is_active: true, created_at: '2026-01-15T12:00:00Z' },
]

function cloneDemoData(data) {
  return JSON.parse(JSON.stringify(data))
}

function demoApiRequest(path, options) {
  const method = (options.method || 'GET').toUpperCase()
  if (method !== 'GET') {
    throw new Error('El inicio rápido es solo una demostración: los cambios no se guardan. Inicia sesión con una cuenta para guardar datos.')
  }

  const pathname = path.split('?')[0]
  if (pathname === '/health') return { status: 'ok', database: 'ok' }
  if (pathname === '/autores') return cloneDemoData([demoAuthor])
  if (pathname === '/categorias') return cloneDemoData([demoCategory])
  if (pathname === '/socios') return cloneDemoData([demoMember])
  if (pathname === '/libros') return cloneDemoData([demoBook])
  if (pathname === '/prestamos') return cloneDemoData([demoLoan])
  if (pathname === '/solicitudes') {
    return cloneDemoData(user.value?.role === 'bibliotecario' ? [demoRequest] : [])
  }
  if (pathname === '/productos') return cloneDemoData([demoProduct])
  if (pathname === '/categorias/1/productos') return cloneDemoData([demoProduct])
  if (pathname === '/usuarios/me') return cloneDemoData(user.value)
  if (pathname === '/usuarios') {
    return { items: cloneDemoData(demoUsers), total: demoUsers.length, page: 1, page_size: 10 }
  }

  const match = pathname.match(/^\/(autores|categorias|socios|libros|prestamos|solicitudes|productos|usuarios)\/(\d+)$/)
  if (match) {
    const collections = {
      autores: [demoAuthor],
      categorias: [demoCategory],
      socios: [demoMember],
      libros: [demoBook],
      prestamos: [demoLoan],
      solicitudes: [demoRequest],
      productos: [demoProduct],
      usuarios: demoUsers,
    }
    const item = collections[match[1]].find((row) => row.id === Number(match[2]))
    if (item) return cloneDemoData(item)
  }

  throw new Error(`La vista de demostración no tiene datos para ${pathname}.`)
}

function clearSession() {
  accessToken.value = ''
  refreshToken.value = ''
  user.value = null
  demoMode.value = false
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
}

function startQuickDemo(role) {
  clearSession()
  errorMessage.value = ''
  successMessage.value = ''
  demoMode.value = true
  user.value = role === 'bibliotecario'
    ? cloneDemoData(demoUsers[0])
    : cloneDemoData(demoUsers[1])
}

function responseError(payload, fallback) {
  if (typeof payload?.detail === 'string') return payload.detail
  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg || 'Dato inválido').join('. ')
  }
  return fallback
}

async function refreshAccessToken() {
  if (!refreshToken.value) return false
  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken.value }),
    })
    if (!response.ok) return false
    const tokens = await response.json()
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    sessionStorage.setItem('access_token', tokens.access_token)
    sessionStorage.setItem('refresh_token', tokens.refresh_token)
    return true
  } catch {
    return false
  }
}

async function apiRequest(path, options = {}, canRefresh = true) {
  if (demoMode.value) return demoApiRequest(path, options)

  const headers = new Headers(options.headers || {})
  if (accessToken.value) headers.set('Authorization', `Bearer ${accessToken.value}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (
    response.status === 401 &&
    canRefresh &&
    refreshToken.value &&
    path !== '/auth/login' &&
    path !== '/auth/refresh'
  ) {
    if (await refreshAccessToken()) return apiRequest(path, options, false)
    clearSession()
  }

  if (!response.ok) {
    const body = await response.text()
    let message = `Error HTTP ${response.status}`
    if (body) {
      try {
        message = responseError(JSON.parse(body), message)
      } catch {
        message = body
      }
    }
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}

async function login() {
  busy.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const tokens = await apiRequest('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    sessionStorage.setItem('access_token', tokens.access_token)
    sessionStorage.setItem('refresh_token', tokens.refresh_token)
    user.value = await apiRequest('/auth/me')
    password.value = ''
  } catch (error) {
    clearSession()
    errorMessage.value = error instanceof Error ? error.message : String(error)
  } finally {
    busy.value = false
  }
}

async function register() {
  errorMessage.value = ''
  successMessage.value = ''
  if (password.value !== passwordConfirmation.value) {
    errorMessage.value = 'Las contraseñas no coinciden.'
    return
  }

  busy.value = true
  try {
    await apiRequest('/auth/registro', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre: name.value,
        email: email.value,
        password: password.value,
      }),
    })
    authMode.value = 'login'
    name.value = ''
    password.value = ''
    passwordConfirmation.value = ''
    successMessage.value = 'Cuenta creada. Ya puedes iniciar sesión.'
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
  } finally {
    busy.value = false
  }
}

async function logout() {
  if (demoMode.value) {
    clearSession()
    return
  }

  errorMessage.value = ''
  try {
    if (refreshToken.value) {
      await apiRequest('/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken.value }),
      })
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
  } finally {
    clearSession()
  }
}

onMounted(async () => {
  if (accessToken.value) {
    try {
      user.value = await apiRequest('/auth/me')
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : String(error)
      clearSession()
    }
  }
  checkingSession.value = false
})
</script>

<template>
  <AdminDashboard
    v-if="user"
    :api-request="apiRequest"
    :user="user"
    :demo-mode="demoMode"
    @logout="logout"
  />

  <main v-else class="auth-shell">
    <div class="auth-brand"><span class="brand-mark">B</span><span>Biblioteca</span></div>
    <section class="auth-card">
      <div class="auth-intro">
        <p class="eyebrow">CATÁLOGO DIGITAL</p>
        <h1>{{ authMode === 'login' ? 'Tu biblioteca,' : 'Únete a la' }}<br /><em>en buenas manos.</em></h1>
        <p>Inicia sesión con tu cuenta o explora una vista de demostración de la biblioteca.</p>
      </div>

      <div v-if="errorMessage" class="notice notice-error" role="alert">{{ errorMessage }}</div>
      <div v-if="successMessage" class="notice notice-success" role="status">{{ successMessage }}</div>
      <div v-if="checkingSession" class="loading-state">Verificando sesión…</div>

      <template v-else>
        <form v-if="authMode === 'login'" class="auth-form" @submit.prevent="login">
          <label>Correo electrónico
            <input v-model.trim="email" type="email" autocomplete="username" required />
          </label>
          <label>Contraseña
            <input v-model="password" type="password" autocomplete="current-password" required />
          </label>
          <button class="button button-primary" type="submit" :disabled="busy">
            {{ busy ? 'Conectando…' : 'Iniciar sesión' }} <span aria-hidden="true">→</span>
          </button>
        </form>

        <form v-else class="auth-form" @submit.prevent="register">
          <label>Nombre
            <input v-model.trim="name" autocomplete="name" maxlength="120" required />
          </label>
          <label>Correo electrónico
            <input v-model.trim="email" type="email" autocomplete="email" required />
          </label>
          <label>Contraseña
            <input v-model="password" type="password" autocomplete="new-password" minlength="8" maxlength="128" required />
          </label>
          <label>Confirmar contraseña
            <input v-model="passwordConfirmation" type="password" autocomplete="new-password" minlength="8" maxlength="128" required />
          </label>
          <button class="button button-primary" type="submit" :disabled="busy">
            {{ busy ? 'Creando cuenta…' : 'Crear cuenta' }} <span aria-hidden="true">→</span>
          </button>
        </form>

        <div v-if="authMode === 'login'" class="quick-start">
          <p>Inicio rápido <span>Demostración sin guardar datos</span></p>
          <div class="quick-start-buttons">
            <button class="button button-secondary" type="button" :disabled="busy" @click="startQuickDemo('bibliotecario')">Bibliotecario</button>
            <button class="button button-secondary" type="button" :disabled="busy" @click="startQuickDemo('cliente')">Usuario</button>
          </div>
          <small>Para guardar cambios, inicia sesión o crea una cuenta.</small>
        </div>

        <button class="auth-switch" :disabled="busy" @click="authMode = authMode === 'login' ? 'register' : 'login'; errorMessage = ''; successMessage = ''">
          {{ authMode === 'login' ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión' }}
        </button>
      </template>
    </section>
    <footer class="auth-footer">Biblioteca · Gestión integral de catálogo</footer>
  </main>
</template>
