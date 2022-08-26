const [entry] = performance.getEntriesByType("navigation");
if (entry["type"] === "back_forward")
    location.reload();

function init() {
  document.body.addEventListener('click', menu_close, true);
};
    
function menu_close(event) {
  var _opened = document.getElementById("navbarToggle").classList.contains("show");
  if (_opened === true && event.target.classList.contains("nav-item") === false ) {
    document.getElementById("navbar-toggle-button").click();
    event.preventDefault();
  }
  var _card_target = document.getElementById("collapseDesc")
  if (_card_target != null) {
    var _card_opened = _card_target.classList.contains("show");
    if (_card_opened === true && event.target.classList.contains("js-toggle-except") === false ) {
      document.getElementById("collapseToggle").click();
      event.preventDefault();
    }
  }
};

