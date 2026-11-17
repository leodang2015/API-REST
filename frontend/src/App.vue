<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
const accessToken = ref(sessionStorage.getItem('access_token') || '')
const refreshToken = ref(sessionStorage.getItem('refresh_token') || '')
const isAuthenticated = computed(() => Boolean(accessToken.value))
const busy = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const authMode = ref('login')
const name = ref('')
const email = ref('')
const password = ref('')
const passwordConfirmation = ref('')
const authors = ref([])
const categories = ref([])
const selectedFile = ref(null)
const previewUrl = ref('')
const fileInput = ref(null)
const createdBook = ref(null)

const bookForm = reactive({
  titulo: '',
  isbn: '',
  descripcion: '',
  anio_publicacion: '',
  ejemplares: 1,
  disponible: 1,
  autor_id: '',
  categoria_ids: [],
})

const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp'])

function clearSession() {
  accessToken.value = ''
  refreshToken.value = ''
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
  authors.value = []
  categories.value = []
}

function formatApiError(payload, fallback) {
  if (typeof payload?.detail === 'string') return payload.detail
  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg || 'Dato inválido').join('. ')
  }
  return fallback
}

async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {})
  if (accessToken.value) headers.set('Authorization', `Bearer ${accessToken.value}`)

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const body = await response.text()
    let message = `Error HTTP ${response.status}`
    if (body) {
      try {
        message = formatApiError(JSON.parse(body), message)
      } catch {
        message = body
      }
    }
    if (response.status === 401) clearSession()
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}

async function loadCatalog() {
  const [authorList, categoryList] = await Promise.all([
    apiRequest('/autores'),
    apiRequest('/categorias'),
  ])
  authors.value = authorList
  categories.value = categoryList
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
    password.value = ''
    await loadCatalog()
    successMessage.value = 'Sesión iniciada. Ya puedes registrar libros.'
  } catch (error) {
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
    successMessage.value =
      'Cuenta creada. Ya puedes iniciar sesión. Para registrar libros necesitas una cuenta administradora.'
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
  } finally {
    busy.value = false
  }
}

async function logout() {
  busy.value = true
  errorMessage.value = ''
  try {
    if (refreshToken.value) {
      await apiRequest('/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken.value }),
      })
    }
    clearSession()
    successMessage.value = 'Sesión cerrada.'
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
    clearSession()
  } finally {
    busy.value = false
  }
}

function selectFile(event) {
  const file = event.target.files?.[0] || null
  errorMessage.value = ''
  successMessage.value = ''
  if (file && !allowedTypes.has(file.type)) {
    errorMessage.value = 'Selecciona una imagen JPEG, PNG o WebP.'
    event.target.value = ''
    selectedFile.value = null
    return
  }
  selectedFile.value = file
}

watch(selectedFile, (file) => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = file ? URL.createObjectURL(file) : ''
})

async function createBook() {
  busy.value = true
  errorMessage.value = ''
  successMessage.value = ''
  createdBook.value = null

  try {
    const formData = new FormData()
    formData.append('titulo', bookForm.titulo)
    formData.append('isbn', bookForm.isbn)
    formData.append('autor_id', String(bookForm.autor_id))
    formData.append('ejemplares', String(bookForm.ejemplares))
    formData.append('disponible', String(bookForm.disponible))
    if (bookForm.descripcion.trim()) formData.append('descripcion', bookForm.descripcion.trim())
    if (bookForm.anio_publicacion) {
      formData.append('anio_publicacion', String(bookForm.anio_publicacion))
    }
    bookForm.categoria_ids.forEach((id) => formData.append('categoria_ids', String(id)))
    formData.append('archivo_portada', selectedFile.value)

    createdBook.value = await apiRequest('/libros', {
      method: 'POST',
      body: formData,
    })
    successMessage.value = 'Libro creado y portada guardada en Cloudinary.'
    Object.assign(bookForm, {
      titulo: '',
      isbn: '',
      descripcion: '',
      anio_publicacion: '',
      ejemplares: 1,
      disponible: 1,
      autor_id: '',
      categoria_ids: [],
    })
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  if (!accessToken.value) return
  try {
    await loadCatalog()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error)
  }
})

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<template>
  <main class="page-shell">
    <header class="topbar">
      <a class="brand" href="#" aria-label="Biblioteca, inicio">
        <span class="brand-mark">B</span>
        <span>Biblioteca<span class="brand-subtitle">Panel de administración</span></span>
      </a>
      <button v-if="isAuthenticated" class="button button-quiet" :disabled="busy" @click="logout">
        Cerrar sesión
      </button>
    </header>

    <section class="intro">
      <p class="eyebrow">CATÁLOGO DIGITAL</p>
      <h1>Una nueva historia<br /><span>empieza aquí.</span></h1>
      <p class="intro-copy">
        Registra libros y guarda sus portadas directamente en tu biblioteca.
      </p>
    </section>

    <div v-if="errorMessage" class="notice notice-error" role="alert">
      <span class="notice-icon">!</span>{{ errorMessage }}
    </div>
    <div v-if="successMessage" class="notice notice-success" role="status">
      <span class="notice-icon">✓</span>{{ successMessage }}
    </div>

    <section v-if="!isAuthenticated" class="panel login-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ authMode === 'login' ? 'ACCESO SEGURO' : 'ÚNETE A LA BIBLIOTECA' }}</p>
          <h2>{{ authMode === 'login' ? 'Inicia sesión' : 'Crea tu cuenta' }}</h2>
        </div>
        <span class="step-number">01</span>
      </div>
      <p class="muted">
        {{
          authMode === 'login'
            ? 'Ingresa con tu cuenta. Para gestionar el catálogo necesitas rol administrador.'
            : 'Regístrate para crear una cuenta de usuario.'
        }}
      </p>
      <form v-if="authMode === 'login'" class="stack-form" @submit.prevent="login">
        <label>
          Correo electrónico
          <input v-model.trim="email" type="email" autocomplete="username" required />
        </label>
        <label>
          Contraseña
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <button class="button button-primary" type="submit" :disabled="busy">
          {{ busy ? 'Conectando…' : 'Entrar al catálogo' }}
          <span aria-hidden="true">→</span>
        </button>
      </form>
      <form v-else class="stack-form" @submit.prevent="register">
        <label>
          Nombre
          <input v-model.trim="name" autocomplete="name" maxlength="120" required />
        </label>
        <label>
          Correo electrónico
          <input v-model.trim="email" type="email" autocomplete="email" required />
        </label>
        <label>
          Contraseña
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
            required
          />
        </label>
        <label>
          Confirmar contraseña
          <input
            v-model="passwordConfirmation"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
            required
          />
        </label>
        <button class="button button-primary" type="submit" :disabled="busy">
          {{ busy ? 'Creando cuenta…' : 'Registrarme' }}
          <span aria-hidden="true">→</span>
        </button>
      </form>
      <button
        class="auth-switch"
        type="button"
        :disabled="busy"
        @click="authMode = authMode === 'login' ? 'register' : 'login'; errorMessage = ''; successMessage = ''"
      >
        {{
          authMode === 'login'
            ? '¿No tienes cuenta? Regístrate'
            : '¿Ya tienes cuenta? Inicia sesión'
        }}
      </button>
    </section>

    <section v-else class="panel book-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">NUEVO REGISTRO</p>
          <h2>Agregar un libro</h2>
        </div>
        <span class="step-number">02</span>
      </div>
      <p class="muted">Completa los datos y adjunta la portada como archivo de imagen.</p>

      <form class="book-form" @submit.prevent="createBook">
        <div class="form-grid">
          <label class="field-wide">
            Título
            <input v-model.trim="bookForm.titulo" maxlength="150" required />
          </label>
          <label>
            ISBN
            <input v-model.trim="bookForm.isbn" minlength="8" maxlength="20" required />
          </label>
          <label>
            Autor
            <select v-model="bookForm.autor_id" required>
              <option disabled value="">Selecciona un autor</option>
              <option v-for="author in authors" :key="author.id" :value="String(author.id)">
                {{ author.nombre }}
              </option>
            </select>
          </label>
          <label>
            Año de publicación
            <input
              v-model="bookForm.anio_publicacion"
              type="number"
              min="1000"
              placeholder="Opcional"
            />
          </label>
          <label>
            Ejemplares
            <input v-model.number="bookForm.ejemplares" type="number" min="1" required />
          </label>
          <label>
            Disponibles
            <input
              v-model.number="bookForm.disponible"
              type="number"
              min="0"
              :max="bookForm.ejemplares"
              required
            />
          </label>
          <label class="field-wide">
            Descripción
            <textarea v-model.trim="bookForm.descripcion" maxlength="500" rows="3" />
          </label>
        </div>

        <fieldset class="category-fieldset">
          <legend>Categorías <span class="optional">(opcional)</span></legend>
          <div v-if="categories.length" class="category-list">
            <label v-for="category in categories" :key="category.id" class="category-option">
              <input v-model="bookForm.categoria_ids" type="checkbox" :value="category.id" />
              <span>{{ category.nombre }}</span>
            </label>
          </div>
          <p v-else class="muted small">No hay categorías registradas.</p>
        </fieldset>

        <div class="upload-row">
          <div class="upload-control">
            <label class="upload-label" for="cover-file">Portada del libro</label>
            <input
              id="cover-file"
              ref="fileInput"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              required
              @change="selectFile"
            />
            <p class="hint">Formatos admitidos: JPG, PNG y WebP.</p>
          </div>
          <img v-if="previewUrl" class="cover-preview" :src="previewUrl" alt="Vista previa de portada" />
        </div>

        <button class="button button-primary submit-button" type="submit" :disabled="busy">
          {{ busy ? 'Guardando libro y portada…' : 'Crear libro' }}
          <span aria-hidden="true">→</span>
        </button>
      </form>
    </section>

    <section v-if="createdBook" class="created-card" aria-live="polite">
      <img
        v-if="createdBook.portada_url"
        :src="createdBook.portada_url"
        :alt="`Portada de ${createdBook.titulo}`"
      />
      <div>
        <p class="eyebrow">LIBRO REGISTRADO</p>
        <h2>{{ createdBook.titulo }}</h2>
        <p class="muted">ISBN {{ createdBook.isbn }}</p>
        <a v-if="createdBook.portada_url" :href="createdBook.portada_url" target="_blank" rel="noopener">
          Ver imagen en Cloudinary
        </a>
      </div>
    </section>

    <footer>Biblioteca · Gestión de catálogo</footer>
  </main>
</template>
