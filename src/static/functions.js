const handleAlerts = (type, msg) => {
    const alert = document.createElement('div')
    alert.className = `alert alert-${type}`
    alert.setAttribute('role', 'alert')
    alert.textContent = msg
    alertBox.replaceChildren(alert)
}
