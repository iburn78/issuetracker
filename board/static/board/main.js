function init() {
  document.body.addEventListener('click', menu_close, true);
};

function menu_close(event) {
  var _opened = document.getElementById("navbarToggle").classList.contains("show");
  if (_opened === true && event.target.classList.contains("nav-item") === false ) {
    document.getElementById("navbar-toggle-button").click();
    event.preventDefault();
  }
};

document.querySelectorAll('.color-element').forEach(element => {
  let bg_color = 'null';
  element.addEventListener('click', function(){
    this.attributes['class'].value.split(" ").forEach(item => {
      if (item.startsWith('bg')) { bg_color = item; };
    });
    document.getElementById('card-create-container').style.backgroundColor = getComputedStyle(this).backgroundColor;
    // card_color is hidden and it's id is set as id_card_color; card_color is input field's name
    document.getElementById('id_card_color').value = getComputedStyle(this).backgroundColor;
    bootstrap.Modal.getInstance(document.getElementById('colorModal')).hide();
  }); 
});


