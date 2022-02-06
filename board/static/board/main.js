function init() {
  document.body.addEventListener('click', close, true);
};

function close(event) {
  var _opened = document.getElementById("navbarToggle").classList.contains("show");
  if (_opened === true && event.target.classList.contains("nav-item") === false ) {
    document.getElementById("navbar-toggle-button").click();
    event.preventDefault();
  }
};
