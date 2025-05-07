// Función para confirmar eliminación
function confirmarEliminacion(mensaje) {
    return confirm(mensaje || "¿Estás seguro de que deseas eliminar este elemento?")
  }
  
  // Función para inicializar tooltips de Bootstrap
  document.addEventListener("DOMContentLoaded", () => {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
  })
  
  // Función para mostrar/ocultar campos adicionales según el tipo de reporte
  document.addEventListener("DOMContentLoaded", () => {
    const tipoReporteSelect = document.getElementById("tipo_reporte")
    if (tipoReporteSelect) {
      tipoReporteSelect.addEventListener("change", function () {
        const value = this.value
        const fechaFields = document.getElementById("fecha_fields")
        const categoriaField = document.getElementById("categoria_field")
  
        if (fechaFields) {
          fechaFields.style.display = value === "todos" || value === "historial" ? "flex" : "none"
        }
  
        if (categoriaField) {
          categoriaField.style.display = value === "inventario" ? "block" : "none"
        }
      })
  
      // Trigger change event on load
      tipoReporteSelect.dispatchEvent(new Event("change"))
    }
  })
  
  // Función para validar formularios
  function validarFormulario(formId) {
    const form = document.getElementById(formId)
    if (!form) return true
  
    let isValid = true
    const requiredFields = form.querySelectorAll("[required]")
  
    requiredFields.forEach((field) => {
      if (!field.value.trim()) {
        field.classList.add("is-invalid")
        isValid = false
      } else {
        field.classList.remove("is-invalid")
      }
    })
  
    return isValid
  }
  