function seleccionarCarta(codigo, imagen, asignada) {
  const rol = document.body.dataset.rol;
  const esAdmin = rol === "admin";

  if (!asignada || esAdmin) {
    abrirModal(codigo, `/static/cartas/${imagen}`, asignada);
  } else {
    mostrarAdvertencia("Esta carta ya fue asignada.");
  }
}

function seleccionarAlAzar() {
  const disponibles = Array.from(document.querySelectorAll(".carta img"))
    .filter(img => img.src.includes("reverso.png"));
  if (disponibles.length === 0) {
    mostrarAdvertencia("No hay cartas disponibles.");
    return;
  }
  const random = disponibles[Math.floor(Math.random() * disponibles.length)];
  const codigo = random.alt;
  const imagen = `${codigo}.png`;
  seleccionarCarta(codigo, imagen, false);
}

function abrirModal(codigo, rutaImagen, asignada) {
  const modal = document.getElementById("modalGanador");
  const vista = document.getElementById("cartaSeleccionadaVista");
  const rol = document.body.dataset.rol;
  const esAdmin = rol === "admin";

  // Limpiar campos
  document.getElementById("nombre").value = "";
  document.getElementById("telefono").value = "";

  // Guardar código
  vista.innerHTML = `
    <img src="${rutaImagen}" alt="${codigo}" style="width: 100px;"><br>
    <p><strong>Carta:</strong> ${codigo}</p>
  `;
  vista.dataset.codigo = codigo;
  document.getElementById("codigo").value = codigo;

  // Determinar el modo
  let modo = "registrar";
  if (asignada && esAdmin) {
    modo = "editar";
  }

  document.getElementById("modoOperacion").value = modo;
  document.getElementById("modalTitulo").textContent =
    modo === "registrar" ? "Registrar ganador" : "Editar/eliminar ganador";

  // Mostrar botones según el modo
  document.getElementById("btnGuardar").style.display = "inline-block";
  document.getElementById("btnEliminar").style.display = (modo === "editar") ? "inline-block" : "none";

  // Si se va a editar, precargar datos
  if (modo === "editar") {
    fetch(`/api/carta/${codigo}`)
      .then(res => res.json())
      .then(data => {
        document.getElementById("nombre").value = data.nombre || "";
        document.getElementById("telefono").value = data.telefono || "";
      });
  }

  modal.style.display = "block";
}

function cerrarModal() {
  document.getElementById("modalGanador").style.display = "none";
}

function procesarFormulario(e) {
  e.preventDefault();
  const modo = document.getElementById("modoOperacion").value;
  const codigo = document.getElementById("codigo").value;
  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;

  let url = "";
  let body = `codigo=${encodeURIComponent(codigo)}&nombre=${encodeURIComponent(nombre)}&telefono=${encodeURIComponent(telefono)}`;

  if (modo === "registrar") {
    url = "/asignar";
  } else if (modo === "editar") {
    url = "/editar";
  }

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body
  }).then(() => window.location.reload());
}

function eliminarGanador(e) {
  e.preventDefault();
  const codigo = document.getElementById("codigo").value;

  if (confirm("¿Estás seguro que deseas eliminar esta asignación?")) {
    fetch("/eliminar", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `codigo=${encodeURIComponent(codigo)}`
    }).then(() => window.location.reload());
  }
}

function mostrarAdvertencia(mensaje) {
  const modal = document.getElementById("modalAdvertencia");
  const mensajeElemento = document.getElementById("mensajeAdvertencia");

  mensajeElemento.textContent = mensaje;
  modal.style.display = "block";
}

function cerrarModalAdvertencia() {
  document.getElementById("modalAdvertencia").style.display = "none";
}

function guardarGanador(e) {
  e.preventDefault();  // ✅ Esto evita que haga GET con parámetros en la URL

  const codigo = document.getElementById("cartaSeleccionadaVista").dataset.codigo;
  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;

  fetch("/editar", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `codigo=${encodeURIComponent(codigo)}&nombre=${encodeURIComponent(nombre)}&telefono=${encodeURIComponent(telefono)}`
  })
  .then(() => window.location.reload());
}
