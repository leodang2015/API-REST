<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  apiRequest: { type: Function, required: true },
  user: { type: Object, required: true },
  demoMode: { type: Boolean, default: false },
})
const emit = defineEmits(['logout'])

const isLibrarian = computed(() => props.user.role === 'bibliotecario')
const activeSection = ref('dashboard')
const busy = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const health = ref(null)
const stats = ref({ authors: 0, books: 0, borrowers: 0, loans: 0 })
const recentLoans = ref([])
const resourceRows = ref([])
const resourceDetail = ref(null)
const resourceForm = ref({})
const resourceMode = ref('')
const editingResourceId = ref(null)
const categoryProducts = ref([])
const bookRows = ref([])
const authors = ref([])
const categories = ref([])
const bookDetail = ref(null)
const bookMode = ref('')
const editingBookId = ref(null)
const bookFile = ref(null)
const bookFilters = reactive({ buscar: '', autor_id: '', categoria_id: '' })
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
const borrowers = ref([])
const loanRows = ref([])
const loanDetail = ref(null)
const requestRows = ref([])
const requestDetail = ref(null)
const requestForm = reactive({ solicitud_id: null, fecha_entrega_estimada: '' })
const loanFormOpen = ref(false)
const loanForm = reactive({ socio_id: '', libro_id: '', fecha_limite: '' })
const fineEditId = ref(null)
const fineValue = ref('')
const userPage = ref(1)
const userPageData = ref({ items: [], total: 0, page: 1, page_size: 10 })
const userDetail = ref(null)
const profile = reactive({ nombre: '', email: '' })
const productFilters = reactive({ buscar: '', categoria_id: '', solo_activos: false })

const sections = computed(() => {
  const base = [
    { id: 'dashboard', label: 'Resumen', icon: '⌂' },
    { id: 'autores', label: 'Autores', icon: 'A' },
    { id: 'libros', label: 'Libros', icon: 'L' },
    { id: 'categorias', label: 'Categorías', icon: 'C' },
    { id: 'productos', label: 'Productos', icon: 'P' },
    { id: 'socios', label: 'Socios', icon: 'S' },
    { id: 'solicitudes', label: 'Solicitudes', icon: '⌕' },
    { id: 'prestamos', label: 'Préstamos', icon: '↗' },
    { id: 'usuarios', label: 'Usuarios', icon: 'U' },
    { id: 'perfil', label: 'Mi perfil', icon: '◎' },
  ]
  return isLibrarian.value
    ? base
    : [
        { id: 'dashboard', label: 'Catálogo', icon: '⌂' },
        { id: 'solicitudes', label: 'Mis solicitudes', icon: '⌕' },
        { id: 'perfil', label: 'Mi perfil', icon: '◎' },
      ]
})

const sectionTitles = {
  dashboard: 'Resumen',
  autores: 'Autores',
  libros: 'Libros',
  categorias: 'Categorías',
  productos: 'Productos',
  socios: 'Socios',
  solicitudes: 'Solicitudes',
  prestamos: 'Préstamos',
  usuarios: 'Usuarios',
  perfil: 'Mi perfil',
}

const resources = {
  autores: {
    path: '/autores',
    singular: 'autor',
    plural: 'Autores',
    description: 'Administra autores y su información bibliográfica.',
    defaults: { nombre: '', nacionalidad: '', anio_nacimiento: '' },
    fields: [
      { key: 'nombre', label: 'Nombre', required: true, maxlength: 100 },
      { key: 'nacionalidad', label: 'Nacionalidad', maxlength: 60 },
      { key: 'anio_nacimiento', label: 'Año de nacimiento', type: 'number', min: 1000 },
    ],
    columns: [
      { key: 'nombre', label: 'Nombre' },
      { key: 'nacionalidad', label: 'Nacionalidad' },
      { key: 'anio_nacimiento', label: 'Nacimiento' },
    ],
  },
  categorias: {
    path: '/categorias',
    singular: 'categoría',
    plural: 'Categorías',
    description: 'Organiza el catálogo y los productos por categorías.',
    defaults: { nombre: '', descripcion: '' },
    fields: [
      { key: 'nombre', label: 'Nombre', required: true, minlength: 3, maxlength: 50 },
      { key: 'descripcion', label: 'Descripción', type: 'textarea', maxlength: 200 },
    ],
    columns: [
      { key: 'nombre', label: 'Categoría' },
      { key: 'descripcion', label: 'Descripción' },
    ],
  },
  socios: {
    path: '/socios',
    singular: 'socio',
    plural: 'Socios',
    description: 'Los socios son las personas a quienes se asignan préstamos.',
    defaults: { nombre: '', email: '', telefono: '', activo: true },
    fields: [
      { key: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 120 },
      { key: 'email', label: 'Correo', type: 'email', required: true },
      { key: 'telefono', label: 'Teléfono', maxlength: 30 },
      { key: 'activo', label: 'Socio activo', type: 'checkbox' },
    ],
    columns: [
      { key: 'nombre', label: 'Nombre' },
      { key: 'email', label: 'Correo' },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'activo', label: 'Estado' },
    ],
  },
  productos: {
    path: '/productos',
    singular: 'producto',
    plural: 'Productos',
    description: 'Gestiona productos, precios, stock y su categoría.',
    defaults: { nombre: '', descripcion: '', precio: '', stock: 0, activo: true, categoria_id: '' },
    fields: [
      { key: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 100 },
      { key: 'descripcion', label: 'Descripción', type: 'textarea', maxlength: 300 },
      { key: 'precio', label: 'Precio', type: 'number', min: 0.01, step: 0.01, required: true },
      { key: 'stock', label: 'Stock', type: 'number', min: 0, step: 1 },
      { key: 'categoria_id', label: 'Categoría', type: 'category', required: true },
      { key: 'activo', label: 'Producto activo', type: 'checkbox' },
    ],
    columns: [
      { key: 'nombre', label: 'Producto' },
      { key: 'categoria.nombre', label: 'Categoría' },
      { key: 'precio', label: 'Precio' },
      { key: 'stock', label: 'Stock' },
      { key: 'activo', label: 'Estado' },
    ],
  },
}

const currentResource = computed(() => resources[activeSection.value] || null)

function setNotice(message, isError = false) {
  errorMessage.value = isError ? message : ''
  successMessage.value = isError ? '' : message
}

function errorText(error) {
  return error instanceof Error ? error.message : String(error)
}

function resetResourceForm() {
  resourceMode.value = ''
  editingResourceId.value = null
  resourceForm.value = {}
}

function resetBookForm() {
  bookMode.value = ''
  editingBookId.value = null
  bookFile.value = null
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
}

function localDateAfterDays(days) {
  const date = new Date(Date.now() + days * 24 * 60 * 60 * 1000)
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

async function loadDashboard() {
  health.value = await props.apiRequest('/health')
  if (!isLibrarian.value) {
    const [books, requests] = await Promise.all([
      props.apiRequest('/libros'),
      props.apiRequest('/solicitudes'),
    ])
    bookRows.value = books
    requestRows.value = requests
    return
  }
  const [authorsList, books, borrowersList, loans] = await Promise.all([
    props.apiRequest('/autores'),
    props.apiRequest('/libros'),
    props.apiRequest('/socios'),
    props.apiRequest('/prestamos'),
  ])
  stats.value = {
    authors: authorsList.length,
    books: books.length,
    borrowers: borrowersList.length,
    loans: loans.length,
  }
  recentLoans.value = loans.slice(0, 5)
}

async function loadResourceSection() {
  const name = activeSection.value
  const config = resources[name]
  if (!config) return
  resetResourceForm()
  resourceDetail.value = null
  categoryProducts.value = []
  if (name === 'productos') {
    await loadCategories()
    await loadProducts()
  } else {
    resourceRows.value = await props.apiRequest(config.path)
  }
}

async function loadCategories() {
  categories.value = await props.apiRequest('/categorias')
}

async function loadProducts() {
  const query = new URLSearchParams()
  if (productFilters.buscar.trim()) query.set('buscar', productFilters.buscar.trim())
  if (productFilters.categoria_id) query.set('categoria_id', productFilters.categoria_id)
  if (productFilters.solo_activos) query.set('solo_activos', 'true')
  const suffix = query.size ? `?${query.toString()}` : ''
  resourceRows.value = await props.apiRequest(`/productos${suffix}`)
}

async function loadBooks() {
  const query = new URLSearchParams()
  if (bookFilters.buscar.trim()) query.set('buscar', bookFilters.buscar.trim())
  if (bookFilters.autor_id) query.set('autor_id', bookFilters.autor_id)
  if (bookFilters.categoria_id) query.set('categoria_id', bookFilters.categoria_id)
  const suffix = query.size ? `?${query.toString()}` : ''
  const [items, authorList, categoryList] = await Promise.all([
    props.apiRequest(`/libros${suffix}`),
    props.apiRequest('/autores'),
    props.apiRequest('/categorias'),
  ])
  bookRows.value = items
  authors.value = authorList
  categories.value = categoryList
}

async function loadLoans() {
  const [loans, members, books] = await Promise.all([
    props.apiRequest('/prestamos'),
    props.apiRequest('/socios'),
    props.apiRequest('/libros'),
  ])
  loanRows.value = loans
  borrowers.value = members
  bookRows.value = books
  loanDetail.value = null
  loanFormOpen.value = false
}

async function loadRequests() {
  requestRows.value = await props.apiRequest('/solicitudes')
  requestDetail.value = null
}

async function loadUsers() {
  userPageData.value = await props.apiRequest(`/usuarios?page=${userPage.value}&page_size=10`)
  userDetail.value = null
}

async function loadProfile() {
  const current = await props.apiRequest('/usuarios/me')
  profile.nombre = current.nombre
  profile.email = current.email
}

async function loadSection() {
  errorMessage.value = ''
  successMessage.value = ''
  busy.value = true
  try {
    if (activeSection.value === 'dashboard') await loadDashboard()
    else if (activeSection.value === 'libros') await loadBooks()
    else if (activeSection.value === 'solicitudes') await loadRequests()
    else if (activeSection.value === 'prestamos') await loadLoans()
    else if (activeSection.value === 'usuarios') await loadUsers()
    else if (activeSection.value === 'perfil') await loadProfile()
    else await loadResourceSection()
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function navigate(section) {
  activeSection.value = section
  resetResourceForm()
  resetBookForm()
  await loadSection()
}

function beginResourceCreate() {
  resourceForm.value = { ...resources[activeSection.value].defaults }
  resourceDetail.value = null
  editingResourceId.value = null
  resourceMode.value = 'create'
  errorMessage.value = ''
}

async function beginResourceEdit(row) {
  busy.value = true
  errorMessage.value = ''
  try {
    const config = resources[activeSection.value]
    const item = await props.apiRequest(`${config.path}/${row.id}`)
    resourceDetail.value = item
    const values = { ...config.defaults }
    for (const field of config.fields) {
      const value = field.key === 'categoria_id' ? item.categoria?.id : item[field.key]
      values[field.key] = value ?? (field.type === 'checkbox' ? false : '')
    }
    resourceForm.value = values
    editingResourceId.value = item.id
    resourceMode.value = 'edit'
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

function resourcePayload(config) {
  const payload = {}
  for (const field of config.fields) {
    const value = resourceForm.value[field.key]
    if (field.type === 'checkbox') {
      payload[field.key] = Boolean(value)
    } else if (field.type === 'number' || field.type === 'category') {
      if (value !== '' && value !== null && value !== undefined) {
        payload[field.key] = Number(value)
      }
    } else if (value !== '' && value !== null && value !== undefined) {
      payload[field.key] = value
    }
  }
  return payload
}

async function saveResource() {
  busy.value = true
  errorMessage.value = ''
  try {
    const config = resources[activeSection.value]
    const editing = resourceMode.value === 'edit'
    const path = editing ? `${config.path}/${editingResourceId.value}` : config.path
    await props.apiRequest(path, {
      method: editing ? 'PATCH' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(resourcePayload(config)),
    })
    resetResourceForm()
    await loadResourceSection()
    setNotice(`${config.singular[0].toUpperCase()}${config.singular.slice(1)} ${editing ? 'actualizado' : 'creado'} correctamente.`)
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function showResourceDetail(row) {
  try {
    const config = resources[activeSection.value]
    resourceDetail.value = await props.apiRequest(`${config.path}/${row.id}`)
    categoryProducts.value = []
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function showCategoryProducts() {
  if (!resourceDetail.value) return
  try {
    categoryProducts.value = await props.apiRequest(`/categorias/${resourceDetail.value.id}/productos`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function deleteResource(row) {
  const config = resources[activeSection.value]
  if (!window.confirm(`¿Eliminar este ${config.singular}?`)) return
  try {
    await props.apiRequest(`${config.path}/${row.id}`, { method: 'DELETE' })
    resourceDetail.value = null
    await loadResourceSection()
    setNotice(`${config.singular} eliminado correctamente.`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

function resourceCell(row, key) {
  const value = key.split('.').reduce((result, part) => result?.[part], row)
  if (typeof value === 'boolean') return value ? 'Activo' : 'Inactivo'
  return value ?? '—'
}

async function submitBook() {
  busy.value = true
  errorMessage.value = ''
  try {
    const editing = bookMode.value === 'edit'
    let result
    if (editing) {
      const payload = {
        titulo: bookForm.titulo,
        isbn: bookForm.isbn,
        autor_id: Number(bookForm.autor_id),
        ejemplares: Number(bookForm.ejemplares),
        disponible: Number(bookForm.disponible),
        categoria_ids: bookForm.categoria_ids.map(Number),
      }
      if (bookForm.descripcion.trim()) payload.descripcion = bookForm.descripcion.trim()
      if (bookForm.anio_publicacion) payload.anio_publicacion = Number(bookForm.anio_publicacion)
      result = await props.apiRequest(`/libros/${editingBookId.value}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (bookFile.value) {
        const cover = new FormData()
        cover.append('archivo', bookFile.value)
        await props.apiRequest(`/libros/${editingBookId.value}/portada`, {
          method: 'POST',
          body: cover,
        })
      }
    } else {
      if (!bookFile.value) throw new Error('Selecciona una portada para el libro.')
      const form = new FormData()
      form.append('titulo', bookForm.titulo)
      form.append('isbn', bookForm.isbn)
      form.append('autor_id', String(bookForm.autor_id))
      form.append('ejemplares', String(bookForm.ejemplares))
      form.append('disponible', String(bookForm.disponible))
      if (bookForm.descripcion.trim()) form.append('descripcion', bookForm.descripcion.trim())
      if (bookForm.anio_publicacion) form.append('anio_publicacion', String(bookForm.anio_publicacion))
      bookForm.categoria_ids.forEach((id) => form.append('categoria_ids', String(id)))
      form.append('archivo_portada', bookFile.value)
      result = await props.apiRequest('/libros', { method: 'POST', body: form })
    }
    resetBookForm()
    bookDetail.value = result || null
    await loadBooks()
    setNotice(`Libro ${editing ? 'actualizado' : 'creado'} correctamente.`)
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function editBook(row) {
  busy.value = true
  try {
    const item = await props.apiRequest(`/libros/${row.id}`)
    bookDetail.value = item
    Object.assign(bookForm, {
      titulo: item.titulo,
      isbn: item.isbn,
      descripcion: item.descripcion || '',
      anio_publicacion: item.anio_publicacion || '',
      ejemplares: item.ejemplares,
      disponible: item.disponible,
      autor_id: String(item.autor.id),
      categoria_ids: item.categorias.map((category) => category.id),
    })
    editingBookId.value = item.id
    bookMode.value = 'edit'
    bookFile.value = null
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function showBookDetail(row) {
  try {
    bookDetail.value = await props.apiRequest(`/libros/${row.id}`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function deleteBook(row) {
  if (!window.confirm(`¿Eliminar "${row.titulo}"?`)) return
  try {
    await props.apiRequest(`/libros/${row.id}`, { method: 'DELETE' })
    bookDetail.value = null
    await loadBooks()
    setNotice('Libro eliminado correctamente.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function showCatalog() {
  busy.value = true
  try {
    const [books, products] = await Promise.all([
      props.apiRequest('/libros'),
      props.apiRequest('/productos?solo_activos=true'),
    ])
    bookRows.value = books
    resourceRows.value = products
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

function openLoanForm() {
  loanDetail.value = null
  loanFormOpen.value = true
  Object.assign(loanForm, { socio_id: '', libro_id: '', fecha_limite: localDateAfterDays(14) })
}

async function createLoan() {
  busy.value = true
  try {
    await props.apiRequest('/prestamos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        socio_id: Number(loanForm.socio_id),
        libro_id: Number(loanForm.libro_id),
        fecha_limite: new Date(loanForm.fecha_limite).toISOString(),
      }),
    })
    loanFormOpen.value = false
    await loadLoans()
    setNotice('Préstamo registrado. El ejemplar disponible se actualizó.')
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function showLoanDetail(row) {
  try {
    loanDetail.value = await props.apiRequest(`/prestamos/${row.id}`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function returnLoan(loan) {
  if (!window.confirm(`¿Registrar la devolución de "${loan.libro.titulo}"?`)) return
  try {
    await props.apiRequest(`/prestamos/${loan.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fecha_devolucion: new Date().toISOString() }),
    })
    await loadLoans()
    setNotice('Devolución registrada y multa calculada.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function saveFine(loan) {
  try {
    await props.apiRequest(`/prestamos/${loan.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ multa: Number(fineValue.value) }),
    })
    fineEditId.value = null
    await loadLoans()
    setNotice('Multa actualizada.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function deleteLoan(loan) {
  if (!window.confirm('¿Eliminar este préstamo devuelto?')) return
  try {
    await props.apiRequest(`/prestamos/${loan.id}`, { method: 'DELETE' })
    await loadLoans()
    setNotice('Préstamo eliminado.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

function startAcceptRequest(request) {
  requestDetail.value = null
  requestForm.solicitud_id = request.id
  requestForm.fecha_entrega_estimada = localDateAfterDays(2)
}

async function acceptRequest() {
  const requestId = requestForm.solicitud_id
  if (!requestId || !requestForm.fecha_entrega_estimada) return
  busy.value = true
  try {
    await props.apiRequest(`/solicitudes/${requestId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        estado: 'aceptada',
        fecha_entrega_estimada: new Date(requestForm.fecha_entrega_estimada).toISOString(),
      }),
    })
    requestForm.solicitud_id = null
    await loadRequests()
    setNotice('Solicitud aceptada y fecha estimada comunicada al cliente.')
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function rejectRequest(request) {
  if (!window.confirm(`¿Rechazar la solicitud de "${request.libro.titulo}"?`)) return
  busy.value = true
  try {
    await props.apiRequest(`/solicitudes/${request.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estado: 'rechazada' }),
    })
    await loadRequests()
    setNotice('Solicitud rechazada.')
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function requestBook(book) {
  busy.value = true
  try {
    await props.apiRequest('/solicitudes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ libro_id: book.id }),
    })
    await loadDashboard()
    setNotice('Solicitud enviada. El bibliotecario confirmará la fecha estimada de entrega.')
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

async function cancelRequest(request) {
  if (!window.confirm(`¿Cancelar la solicitud de "${request.libro.titulo}"?`)) return
  try {
    await props.apiRequest(`/solicitudes/${request.id}`, { method: 'DELETE' })
    await loadRequests()
    setNotice('Solicitud cancelada.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function showRequestDetail(request) {
  try {
    requestDetail.value = await props.apiRequest(`/solicitudes/${request.id}`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

function requestStatusLabel(status) {
  return {
    pendiente: 'Pendiente',
    aceptada: 'Aceptada',
    rechazada: 'Rechazada',
  }[status] || status
}

function hasPendingRequest(bookId) {
  return requestRows.value.some(
    (request) => request.libro_id === bookId && request.estado === 'pendiente',
  )
}

async function loadUserDetail(row) {
  try {
    userDetail.value = await props.apiRequest(`/usuarios/${row.id}`)
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function deactivateUser(row) {
  if (row.role === 'bibliotecario') {
    setNotice('No se puede desactivar una cuenta de bibliotecario desde esta pantalla.', true)
    return
  }
  if (!window.confirm(`¿Desactivar la cuenta de ${row.nombre}?`)) return
  try {
    await props.apiRequest(`/usuarios/${row.id}`, { method: 'DELETE' })
    await loadUsers()
    setNotice('Cuenta desactivada.')
  } catch (error) {
    setNotice(errorText(error), true)
  }
}

async function changeUserPage(page) {
  userPage.value = page
  await loadUsers()
}

async function saveProfile() {
  busy.value = true
  try {
    const updated = await props.apiRequest('/usuarios/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: profile.nombre, email: profile.email }),
    })
    profile.nombre = updated.nombre
    profile.email = updated.email
    setNotice('Perfil actualizado.')
  } catch (error) {
    setNotice(errorText(error), true)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  await loadSection()
})
</script>

<template>
  <div class="dashboard-shell">
    <aside class="sidebar">
      <a class="brand" href="#" @click.prevent="navigate('dashboard')">
        <span class="brand-mark">B</span>
        <span>Biblioteca<span class="brand-subtitle">Panel de gestión</span></span>
      </a>
      <div class="sidebar-label">MENÚ PRINCIPAL</div>
      <nav class="side-nav" aria-label="Navegación principal">
        <button
          v-for="item in sections"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeSection === item.id }"
          @click="navigate(item.id)"
        >
          <span class="nav-icon">{{ item.icon }}</span>{{ item.label }}
        </button>
      </nav>
      <div class="sidebar-bottom">
        <div class="user-chip">
          <span class="avatar">{{ user.nombre?.slice(0, 1).toUpperCase() }}</span>
          <span class="user-chip-text"><strong>{{ user.nombre }}</strong><small>{{ isLibrarian ? 'Bibliotecario' : 'Cliente' }}</small></span>
        </div>
        <button class="logout-button" @click="emit('logout')">{{ demoMode ? 'Salir de demostración' : 'Cerrar sesión' }} <span>↗</span></button>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ isLibrarian ? 'BIBLIOTECA · ADMINISTRACIÓN' : 'BIBLIOTECA · CLIENTES' }}</p>
          <h1>{{ activeSection === 'dashboard' && !isLibrarian ? 'Catálogo' : activeSection === 'solicitudes' && !isLibrarian ? 'Mis solicitudes' : sectionTitles[activeSection] || 'Catálogo' }}</h1>
        </div>
        <div class="topbar-status">
          <template v-if="demoMode">INICIO RÁPIDO · NO SE GUARDAN DATOS</template>
          <template v-else>
            <span class="status-dot" :class="{ offline: health && health.status !== 'ok' }"></span>
            {{ health?.database === 'ok' ? 'Base de datos conectada' : 'Conectando…' }}
          </template>
        </div>
      </header>

      <div v-if="errorMessage" class="notice notice-error" role="alert">
        <span>!</span>{{ errorMessage }}<button aria-label="Cerrar" @click="errorMessage = ''">×</button>
      </div>
      <div v-if="successMessage" class="notice notice-success" role="status">
        <span>✓</span>{{ successMessage }}<button aria-label="Cerrar" @click="successMessage = ''">×</button>
      </div>
      <div v-if="busy" class="loading-line"><span></span>Procesando…</div>

      <template v-if="activeSection === 'dashboard' && isLibrarian">
        <section class="welcome-card">
          <div>
            <p class="eyebrow">PANEL DE CONTROL</p>
            <h2>Hola, {{ user.nombre.split(' ')[0] }}.</h2>
            <p>Gestiona el catálogo y da seguimiento a los préstamos de tu biblioteca.</p>
          </div>
          <span class="welcome-mark">B</span>
        </section>
        <section class="stat-grid" aria-label="Resumen">
          <article class="stat-card"><span class="stat-icon olive">A</span><div><span>Autores</span><strong>{{ stats.authors }}</strong></div></article>
          <article class="stat-card"><span class="stat-icon blue">L</span><div><span>Libros</span><strong>{{ stats.books }}</strong></div></article>
          <article class="stat-card"><span class="stat-icon peach">S</span><div><span>Socios</span><strong>{{ stats.borrowers }}</strong></div></article>
          <article class="stat-card"><span class="stat-icon lilac">↗</span><div><span>Préstamos</span><strong>{{ stats.loans }}</strong></div></article>
        </section>
        <section class="content-card">
          <div class="card-heading"><div><p class="eyebrow">ACTIVIDAD</p><h2>Préstamos recientes</h2></div><button class="button button-secondary" @click="navigate('prestamos')">Ver todos <span>→</span></button></div>
          <div v-if="recentLoans.length" class="table-wrap">
            <table><thead><tr><th>Socio</th><th>Libro</th><th>Fecha límite</th><th>Estado</th></tr></thead>
              <tbody><tr v-for="loan in recentLoans" :key="loan.id"><td>{{ loan.socio.nombre }}</td><td>{{ loan.libro.titulo }}</td><td>{{ new Date(loan.fecha_limite).toLocaleDateString() }}</td><td><span class="badge" :class="loan.devuelto ? 'badge-muted' : 'badge-green'">{{ loan.devuelto ? 'Devuelto' : 'Activo' }}</span></td></tr></tbody>
            </table>
          </div>
          <div v-else class="empty-state">Todavía no hay préstamos registrados.</div>
        </section>
      </template>

      <template v-else-if="activeSection === 'dashboard'">
        <section class="welcome-card">
          <div><p class="eyebrow">CATÁLOGO PARA CLIENTES</p><h2>Hola, {{ user.nombre.split(' ')[0] }}.</h2><p>Solicita un libro y consulta la fecha estimada de entrega que confirme el bibliotecario.</p></div>
        </section>
        <section class="content-card">
          <div class="card-heading"><div><p class="eyebrow">CATÁLOGO</p><h2>Libros disponibles</h2></div></div>
          <div v-if="bookRows.length" class="catalog-grid">
            <article v-for="book in bookRows" :key="book.id" class="catalog-card">
              <img v-if="book.portada_url" :src="book.portada_url" :alt="`Portada de ${book.titulo}`" />
              <div class="catalog-card-body"><h3>{{ book.titulo }}</h3><p>{{ book.autor.nombre }}</p><span>{{ book.disponible }} disponibles</span><button class="button button-primary request-button" :disabled="busy || hasPendingRequest(book.id)" @click="requestBook(book)">{{ hasPendingRequest(book.id) ? 'Solicitud pendiente' : 'Solicitar libro' }}</button></div>
            </article>
          </div>
          <div v-else class="empty-state">No hay libros registrados.</div>
        </section>
      </template>

      <template v-else-if="currentResource">
        <section class="page-intro">
          <div><p class="eyebrow">GESTIÓN DEL CATÁLOGO</p><p>{{ currentResource.description }}</p></div>
          <button class="button button-primary" @click="beginResourceCreate">＋ Agregar {{ currentResource.singular }}</button>
        </section>
        <section v-if="resourceMode" class="content-card form-card">
          <div class="card-heading"><div><p class="eyebrow">{{ resourceMode === 'edit' ? 'ACTUALIZAR' : 'NUEVO REGISTRO' }}</p><h2>{{ resourceMode === 'edit' ? 'Editar' : 'Agregar' }} {{ currentResource.singular }}</h2></div><button class="icon-button" aria-label="Cerrar formulario" @click="resetResourceForm">×</button></div>
          <form class="form-grid" @submit.prevent="saveResource">
            <label v-for="field in currentResource.fields" :key="field.key" :class="{ 'field-wide': field.type === 'textarea' }">
              <span>{{ field.label }}</span>
              <textarea v-if="field.type === 'textarea'" v-model="resourceForm[field.key]" :maxlength="field.maxlength" />
              <select v-else-if="field.type === 'category'" v-model="resourceForm[field.key]" :required="field.required">
                <option value="">Selecciona una categoría</option><option v-for="category in categories" :key="category.id" :value="category.id">{{ category.nombre }}</option>
              </select>
              <input v-else-if="field.type === 'checkbox'" v-model="resourceForm[field.key]" type="checkbox" class="checkbox-input" />
              <input v-else v-model="resourceForm[field.key]" :type="field.type || 'text'" :required="field.required" :minlength="field.minlength" :maxlength="field.maxlength" :min="field.min" :step="field.step" />
            </label>
            <div class="form-actions field-wide"><button class="button button-secondary" type="button" @click="resetResourceForm">Cancelar</button><button class="button button-primary" type="submit" :disabled="busy">{{ resourceMode === 'edit' ? 'Guardar cambios' : 'Crear' }}</button></div>
          </form>
        </section>

        <section class="content-card">
          <div class="table-toolbar">
            <div><p class="eyebrow">REGISTROS</p><h2>{{ currentResource.plural }} <span class="count-pill">{{ resourceRows.length }}</span></h2></div>
            <form v-if="activeSection === 'productos'" class="filter-form" @submit.prevent="loadProducts">
              <input v-model.trim="productFilters.buscar" placeholder="Buscar producto" aria-label="Buscar producto" />
              <select v-model="productFilters.categoria_id" aria-label="Filtrar por categoría"><option value="">Todas las categorías</option><option v-for="category in categories" :key="category.id" :value="String(category.id)">{{ category.nombre }}</option></select>
              <label class="inline-check"><input v-model="productFilters.solo_activos" type="checkbox" /> Activos</label>
              <button class="button button-secondary" type="submit">Filtrar</button>
            </form>
          </div>
          <div v-if="resourceRows.length" class="table-wrap">
            <table>
              <thead><tr><th v-for="column in currentResource.columns" :key="column.key">{{ column.label }}</th><th class="actions-heading">Acciones</th></tr></thead>
              <tbody>
                <tr v-for="row in resourceRows" :key="row.id">
                  <td v-for="column in currentResource.columns" :key="column.key">{{ resourceCell(row, column.key) }}</td>
                  <td class="row-actions">
                    <button class="text-button" @click="showResourceDetail(row)">Ver</button>
                    <button class="text-button" @click="beginResourceEdit(row)">Editar</button>
                    <button class="text-button danger-text" @click="deleteResource(row)">Eliminar</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">No hay registros. Agrega el primero para comenzar.</div>
        </section>

        <section v-if="resourceDetail" class="content-card detail-card">
          <div class="card-heading"><div><p class="eyebrow">DETALLE</p><h2>{{ resourceDetail.nombre || resourceDetail.titulo }}</h2></div><button class="icon-button" aria-label="Cerrar detalle" @click="resourceDetail = null">×</button></div>
          <div class="detail-grid"><div v-for="column in currentResource.columns" :key="column.key"><span>{{ column.label }}</span><strong>{{ resourceCell(resourceDetail, column.key) }}</strong></div></div>
          <button v-if="activeSection === 'categorias'" class="button button-secondary detail-action" @click="showCategoryProducts">Ver productos de esta categoría</button>
          <div v-if="categoryProducts.length" class="category-products"><strong>Productos relacionados</strong><span v-for="product in categoryProducts" :key="product.id">{{ product.nombre }} · ${{ Number(product.precio).toFixed(2) }}</span></div>
        </section>
      </template>

      <template v-else-if="activeSection === 'libros'">
        <section class="page-intro">
          <div><p class="eyebrow">CATÁLOGO DIGITAL</p><p>Registra, filtra y actualiza libros, ejemplares y portadas.</p></div>
          <button class="button button-primary" @click="bookMode = 'create'; bookDetail = null; Object.assign(bookForm, { titulo: '', isbn: '', descripcion: '', anio_publicacion: '', ejemplares: 1, disponible: 1, autor_id: '', categoria_ids: [] }); bookFile = null">＋ Agregar libro</button>
        </section>
        <section v-if="bookMode" class="content-card form-card">
          <div class="card-heading"><div><p class="eyebrow">{{ bookMode === 'edit' ? 'ACTUALIZAR' : 'NUEVO REGISTRO' }}</p><h2>{{ bookMode === 'edit' ? 'Editar libro' : 'Registrar libro' }}</h2></div><button class="icon-button" @click="resetBookForm">×</button></div>
          <form class="form-grid" @submit.prevent="submitBook">
            <label class="field-wide"><span>Título</span><input v-model.trim="bookForm.titulo" minlength="2" maxlength="150" required /></label>
            <label><span>ISBN</span><input v-model.trim="bookForm.isbn" minlength="8" maxlength="20" required /></label>
            <label><span>Autor</span><select v-model="bookForm.autor_id" required><option value="">Selecciona un autor</option><option v-for="author in authors" :key="author.id" :value="String(author.id)">{{ author.nombre }}</option></select></label>
            <label><span>Año de publicación</span><input v-model="bookForm.anio_publicacion" type="number" min="1000" placeholder="Opcional" /></label>
            <label><span>Ejemplares</span><input v-model.number="bookForm.ejemplares" type="number" min="1" required /></label>
            <label><span>Disponibles</span><input v-model.number="bookForm.disponible" type="number" min="0" :max="bookForm.ejemplares" required /></label>
            <label class="field-wide"><span>Descripción</span><textarea v-model.trim="bookForm.descripcion" maxlength="500" /></label>
            <fieldset class="category-fieldset field-wide"><legend>Categorías</legend><label v-for="category in categories" :key="category.id" class="category-option"><input v-model="bookForm.categoria_ids" type="checkbox" :value="category.id" /><span>{{ category.nombre }}</span></label><p v-if="!categories.length" class="hint">Aún no hay categorías.</p></fieldset>
            <label class="field-wide"><span>Portada {{ bookMode === 'edit' ? '(opcional para reemplazar)' : '(requerida)' }}</span><input type="file" accept="image/jpeg,image/png,image/webp" :required="bookMode === 'create'" @change="bookFile = $event.target.files?.[0] || null" /></label>
            <div class="form-actions field-wide"><button class="button button-secondary" type="button" @click="resetBookForm">Cancelar</button><button class="button button-primary" type="submit" :disabled="busy">{{ bookMode === 'edit' ? 'Guardar libro' : 'Crear libro' }}</button></div>
          </form>
        </section>
        <section class="content-card">
          <div class="table-toolbar"><div><p class="eyebrow">CATÁLOGO</p><h2>Libros <span class="count-pill">{{ bookRows.length }}</span></h2></div>
            <form class="filter-form" @submit.prevent="loadBooks"><input v-model.trim="bookFilters.buscar" placeholder="Buscar título" aria-label="Buscar título" /><select v-model="bookFilters.autor_id"><option value="">Todos los autores</option><option v-for="author in authors" :key="author.id" :value="String(author.id)">{{ author.nombre }}</option></select><select v-model="bookFilters.categoria_id"><option value="">Todas las categorías</option><option v-for="category in categories" :key="category.id" :value="String(category.id)">{{ category.nombre }}</option></select><button class="button button-secondary" type="submit">Filtrar</button></form>
          </div>
          <div v-if="bookRows.length" class="table-wrap"><table><thead><tr><th>Libro</th><th>Autor</th><th>ISBN</th><th>Disponibles</th><th>Acciones</th></tr></thead><tbody><tr v-for="book in bookRows" :key="book.id"><td><button class="table-link" @click="showBookDetail(book)">{{ book.titulo }}</button></td><td>{{ book.autor.nombre }}</td><td>{{ book.isbn }}</td><td>{{ book.disponible }} / {{ book.ejemplares }}</td><td class="row-actions"><button class="text-button" @click="showBookDetail(book)">Ver</button><button class="text-button" @click="editBook(book)">Editar</button><button class="text-button danger-text" @click="deleteBook(book)">Eliminar</button></td></tr></tbody></table></div>
          <div v-else class="empty-state">No hay libros que coincidan con el filtro.</div>
        </section>
        <section v-if="bookDetail && !bookMode" class="content-card detail-card"><div class="card-heading"><div><p class="eyebrow">DETALLE DEL LIBRO</p><h2>{{ bookDetail.titulo }}</h2></div><button class="icon-button" @click="bookDetail = null">×</button></div><div class="detail-grid"><div><span>Autor</span><strong>{{ bookDetail.autor.nombre }}</strong></div><div><span>ISBN</span><strong>{{ bookDetail.isbn }}</strong></div><div><span>Ejemplares</span><strong>{{ bookDetail.disponible }} disponibles de {{ bookDetail.ejemplares }}</strong></div><div><span>Categorías</span><strong>{{ bookDetail.categorias.map((item) => item.nombre).join(', ') || '—' }}</strong></div></div><img v-if="bookDetail.portada_url" class="detail-cover" :src="bookDetail.portada_url" :alt="`Portada de ${bookDetail.titulo}`" /><a v-if="bookDetail.portada_url" class="text-button" :href="bookDetail.portada_url" target="_blank" rel="noopener">Ver portada</a></section>
      </template>

      <template v-else-if="activeSection === 'solicitudes'">
        <section class="page-intro">
          <div>
            <p class="eyebrow">{{ isLibrarian ? 'SOLICITUDES DE CLIENTES' : 'SEGUIMIENTO' }}</p>
            <p>{{ isLibrarian ? 'Acepta o rechaza solicitudes y comunica una fecha estimada de entrega.' : 'Consulta el estado de tus solicitudes y la fecha estimada de entrega.' }}</p>
          </div>
        </section>
        <section v-if="isLibrarian && requestForm.solicitud_id" class="content-card form-card">
          <div class="card-heading"><div><p class="eyebrow">ACEPTAR SOLICITUD</p><h2>Fecha estimada de entrega</h2></div><button class="icon-button" @click="requestForm.solicitud_id = null">×</button></div>
          <form class="form-grid" @submit.prevent="acceptRequest">
            <label><span>Entrega estimada</span><input v-model="requestForm.fecha_entrega_estimada" type="datetime-local" required /></label>
            <div class="form-actions field-wide"><button class="button button-secondary" type="button" @click="requestForm.solicitud_id = null">Cancelar</button><button class="button button-primary" type="submit" :disabled="busy">Aceptar y avisar al cliente</button></div>
          </form>
        </section>
        <section class="content-card">
          <div class="table-toolbar"><div><p class="eyebrow">SOLICITUDES</p><h2>{{ isLibrarian ? 'Solicitudes recibidas' : 'Mis solicitudes' }} <span class="count-pill">{{ requestRows.length }}</span></h2></div></div>
          <div v-if="requestRows.length" class="table-wrap">
            <table>
              <thead><tr><th v-if="isLibrarian">Cliente</th><th>Libro</th><th>Solicitada</th><th>Estado</th><th>Entrega estimada</th><th>Acciones</th></tr></thead>
              <tbody>
                <tr v-for="request in requestRows" :key="request.id">
                  <td v-if="isLibrarian">{{ request.socio.nombre }}<br /><small>{{ request.socio.email }}</small></td>
                  <td><button class="table-link" @click="showRequestDetail(request)">{{ request.libro.titulo }}</button></td>
                  <td>{{ new Date(request.fecha_solicitud).toLocaleDateString() }}</td>
                  <td><span class="badge" :class="request.estado === 'pendiente' ? 'badge-blue' : request.estado === 'aceptada' ? 'badge-green' : 'badge-muted'">{{ requestStatusLabel(request.estado) }}</span></td>
                  <td>{{ request.fecha_entrega_estimada ? new Date(request.fecha_entrega_estimada).toLocaleString() : 'Por confirmar' }}</td>
                  <td class="row-actions">
                    <button class="text-button" @click="showRequestDetail(request)">Ver</button>
                    <template v-if="isLibrarian && request.estado === 'pendiente'">
                      <button class="text-button" @click="startAcceptRequest(request)">Aceptar</button>
                      <button class="text-button danger-text" @click="rejectRequest(request)">Rechazar</button>
                    </template>
                    <button v-else-if="!isLibrarian && request.estado === 'pendiente'" class="text-button danger-text" @click="cancelRequest(request)">Cancelar</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">{{ isLibrarian ? 'Todavía no hay solicitudes.' : 'Aún no has solicitado libros.' }}</div>
        </section>
        <section v-if="requestDetail" class="content-card detail-card">
          <div class="card-heading"><div><p class="eyebrow">DETALLE DE SOLICITUD</p><h2>{{ requestDetail.libro.titulo }}</h2></div><button class="icon-button" @click="requestDetail = null">×</button></div>
          <div class="detail-grid">
            <div><span>Estado</span><strong>{{ requestStatusLabel(requestDetail.estado) }}</strong></div>
            <div><span>Solicitada</span><strong>{{ new Date(requestDetail.fecha_solicitud).toLocaleString() }}</strong></div>
            <div><span>Entrega estimada</span><strong>{{ requestDetail.fecha_entrega_estimada ? new Date(requestDetail.fecha_entrega_estimada).toLocaleString() : 'Por confirmar por el bibliotecario' }}</strong></div>
            <div v-if="isLibrarian"><span>Cliente</span><strong>{{ requestDetail.socio.nombre }} · {{ requestDetail.socio.email }}</strong></div>
            <div><span>Disponibilidad actual</span><strong>{{ requestDetail.libro.disponible }} ejemplares</strong></div>
          </div>
        </section>
      </template>

      <template v-else-if="activeSection === 'prestamos'">
        <section class="page-intro"><div><p class="eyebrow">CIRCULACIÓN</p><p>Registra préstamos, devoluciones y multas de los socios.</p></div><button class="button button-primary" @click="openLoanForm">＋ Nuevo préstamo</button></section>
        <section v-if="loanFormOpen" class="content-card form-card"><div class="card-heading"><div><p class="eyebrow">NUEVO PRÉSTAMO</p><h2>Asignar libro a un socio</h2></div><button class="icon-button" @click="loanFormOpen = false">×</button></div><form class="form-grid" @submit.prevent="createLoan"><label><span>Socio</span><select v-model="loanForm.socio_id" required><option value="">Selecciona un socio</option><option v-for="member in borrowers.filter((item) => item.activo)" :key="member.id" :value="String(member.id)">{{ member.nombre }} · {{ member.email }}</option></select></label><label><span>Libro disponible</span><select v-model="loanForm.libro_id" required><option value="">Selecciona un libro</option><option v-for="book in bookRows.filter((item) => item.disponible > 0)" :key="book.id" :value="String(book.id)">{{ book.titulo }} · {{ book.disponible }} disponibles</option></select></label><label><span>Fecha límite</span><input v-model="loanForm.fecha_limite" type="datetime-local" required /></label><div class="form-actions field-wide"><button class="button button-secondary" type="button" @click="loanFormOpen = false">Cancelar</button><button class="button button-primary" type="submit" :disabled="busy">Registrar préstamo</button></div></form></section>
        <section class="content-card"><div class="table-toolbar"><div><p class="eyebrow">MOVIMIENTOS</p><h2>Préstamos <span class="count-pill">{{ loanRows.length }}</span></h2></div></div><div v-if="loanRows.length" class="table-wrap"><table><thead><tr><th>Socio</th><th>Libro</th><th>Fecha préstamo</th><th>Fecha límite</th><th>Multa</th><th>Estado</th><th>Acciones</th></tr></thead><tbody><tr v-for="loan in loanRows" :key="loan.id"><td>{{ loan.socio.nombre }}</td><td><button class="table-link" @click="showLoanDetail(loan)">{{ loan.libro.titulo }}</button></td><td>{{ new Date(loan.fecha_prestamo).toLocaleDateString() }}</td><td>{{ new Date(loan.fecha_limite).toLocaleDateString() }}</td><td>${{ Number(loan.multa).toFixed(2) }}</td><td><span class="badge" :class="loan.devuelto ? 'badge-muted' : 'badge-green'">{{ loan.devuelto ? 'Devuelto' : 'Activo' }}</span></td><td class="row-actions"><button class="text-button" @click="showLoanDetail(loan)">Ver</button><button v-if="!loan.devuelto" class="text-button" @click="returnLoan(loan)">Devolver</button><button v-if="loan.devuelto" class="text-button" @click="fineEditId = loan.id; fineValue = String(loan.multa)">Multa</button><button v-if="loan.devuelto" class="text-button danger-text" @click="deleteLoan(loan)">Eliminar</button><form v-if="fineEditId === loan.id" class="fine-form" @submit.prevent="saveFine(loan)"><input v-model="fineValue" type="number" min="0" step="0.01" aria-label="Multa" required /><button class="text-button" type="submit">Guardar</button><button class="text-button" type="button" @click="fineEditId = null">Cancelar</button></form></td></tr></tbody></table></div><div v-else class="empty-state">No hay préstamos registrados.</div></section>
        <section v-if="loanDetail" class="content-card detail-card"><div class="card-heading"><div><p class="eyebrow">DETALLE DEL PRÉSTAMO</p><h2>{{ loanDetail.socio.nombre }} · {{ loanDetail.libro.titulo }}</h2></div><button class="icon-button" @click="loanDetail = null">×</button></div><div class="detail-grid"><div><span>Socio</span><strong>{{ loanDetail.socio.email }}</strong></div><div><span>Fecha límite</span><strong>{{ new Date(loanDetail.fecha_limite).toLocaleString() }}</strong></div><div><span>Fecha de devolución</span><strong>{{ loanDetail.fecha_devolucion ? new Date(loanDetail.fecha_devolucion).toLocaleString() : 'Pendiente' }}</strong></div><div><span>Multa</span><strong>${{ Number(loanDetail.multa).toFixed(2) }}</strong></div></div></section>
      </template>

      <template v-else-if="activeSection === 'usuarios'">
        <section class="page-intro"><div><p class="eyebrow">ACCESO Y SEGURIDAD</p><p>Consulta cuentas registradas y desactiva cuentas cliente. El registro público crea cuentas cliente; el bibliotecario se asigna de forma administrativa.</p></div></section>
        <section class="content-card"><div class="table-toolbar"><div><p class="eyebrow">CUENTAS</p><h2>Usuarios <span class="count-pill">{{ userPageData.total }}</span></h2></div></div><div v-if="userPageData.items.length" class="table-wrap"><table><thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead><tbody><tr v-for="row in userPageData.items" :key="row.id"><td>{{ row.nombre }}</td><td>{{ row.email }}</td><td><span class="badge" :class="row.role === 'bibliotecario' ? 'badge-blue' : 'badge-muted'">{{ row.role }}</span></td><td>{{ row.is_active ? 'Activo' : 'Inactivo' }}</td><td class="row-actions"><button class="text-button" @click="loadUserDetail(row)">Ver</button><button v-if="row.is_active && row.role !== 'bibliotecario'" class="text-button danger-text" @click="deactivateUser(row)">Desactivar</button></td></tr></tbody></table></div><div v-else class="empty-state">No hay usuarios registrados.</div><div class="pagination"><button class="button button-secondary" :disabled="userPage <= 1" @click="changeUserPage(userPage - 1)">Anterior</button><span>Página {{ userPage }} · {{ userPageData.total }} usuarios</span><button class="button button-secondary" :disabled="userPage * userPageData.page_size >= userPageData.total" @click="changeUserPage(userPage + 1)">Siguiente</button></div></section>
        <section v-if="userDetail" class="content-card detail-card"><div class="card-heading"><div><p class="eyebrow">CUENTA</p><h2>{{ userDetail.nombre }}</h2></div><button class="icon-button" @click="userDetail = null">×</button></div><div class="detail-grid"><div><span>Correo</span><strong>{{ userDetail.email }}</strong></div><div><span>Rol</span><strong>{{ userDetail.role }}</strong></div><div><span>Estado</span><strong>{{ userDetail.is_active ? 'Activo' : 'Inactivo' }}</strong></div><div><span>Registro</span><strong>{{ new Date(userDetail.created_at).toLocaleString() }}</strong></div></div></section>
      </template>

      <template v-else-if="activeSection === 'perfil'">
        <section class="content-card profile-card"><div class="card-heading"><div><p class="eyebrow">CUENTA ACTIVA</p><h2>Datos del perfil</h2></div><span class="badge" :class="isLibrarian ? 'badge-blue' : 'badge-muted'">{{ user.role }}</span></div><form class="profile-form" @submit.prevent="saveProfile"><label>Nombre<input v-model.trim="profile.nombre" maxlength="120" required /></label><label>Correo electrónico<input v-model.trim="profile.email" type="email" required /></label><button class="button button-primary" type="submit" :disabled="busy">Guardar cambios</button></form></section>
      </template>

      <footer class="dashboard-footer">Biblioteca · Gestión integral de catálogo <span>API <span :class="{ 'health-ok': health?.status === 'ok' }">{{ health?.status || '—' }}</span></span></footer>
    </main>
  </div>
</template>
